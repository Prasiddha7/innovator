import uuid
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Sum, Count

from kms.models import (
    Teacher, School, TeacherCompensationRule, TeacherAttendance,
    TeacherInvoice, InvoiceStatus, TeacherClassAssignment,
)
from kms.permissions import IsAdmin
from kms.authentication import CustomJWTAuthentication


def _resolve_school(value):
    """Find school by UUID or name."""
    if not value:
        return None
    try:
        return School.objects.get(id=value)
    except (School.DoesNotExist, ValueError):
        pass
    try:
        lookup = uuid.UUID(str(value))
        return School.objects.get(id=lookup)
    except (ValueError, School.DoesNotExist):
        pass
    try:
        return School.objects.get(name__iexact=value)
    except School.DoesNotExist:
        return None


def _resolve_teacher(value):
    """Find teacher by UUID, user UUID, or name."""
    if not value:
        return None
    try:
        return Teacher.objects.get(id=value)
    except (Teacher.DoesNotExist, ValueError):
        pass
    try:
        lookup = uuid.UUID(str(value))
        return Teacher.objects.get(id=lookup)
    except (ValueError, Teacher.DoesNotExist):
        pass
    try:
        return Teacher.objects.filter(name__iexact=value).first()
    except Exception:
        return None


def _generate_invoice_number(year, month):
    """Generate a unique invoice number like INV-2026-03-001."""
    prefix = f"INV-{year}-{month:02d}"
    last_invoice = (
        TeacherInvoice.objects
        .filter(invoice_number__startswith=prefix)
        .order_by('-invoice_number')
        .first()
    )
    if last_invoice:
        try:
            last_seq = int(last_invoice.invoice_number.split('-')[-1])
            next_seq = last_seq + 1
        except (ValueError, IndexError):
            next_seq = 1
    else:
        next_seq = 1
    return f"{prefix}-{next_seq:03d}"


# ==========================================================================
# GENERATE TEACHER INVOICES
# ==========================================================================

class GenerateTeacherInvoiceView(APIView):
    """
    POST: Generate teacher invoices for a school.

    Payload:
    {
        "school": "uuid-or-name",       (required)
        "month": 3,                      (required)
        "year": 2026,                    (required)
        "teacher": "uuid-or-name",       (optional - generate for one teacher)
        "tax_rate": 13.00                (optional - defaults to 13%)
    }
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        school_val = request.data.get('school')
        month = request.data.get('month')
        year = request.data.get('year')
        teacher_val = request.data.get('teacher')
        tax_rate = Decimal(str(request.data.get('tax_rate', '13.00')))

        # Validate required fields
        if not school_val or not month or not year:
            return Response(
                {"error": "school, month, and year are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            month = int(month)
            year = int(year)
        except (ValueError, TypeError):
            return Response(
                {"error": "month and year must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if month < 1 or month > 12:
            return Response(
                {"error": "month must be between 1 and 12."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resolve school
        school = _resolve_school(school_val)
        if not school:
            return Response(
                {"error": f"School '{school_val}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get compensation rules for this school
        rules = TeacherCompensationRule.objects.filter(school=school, is_active=True)

        # Optionally filter by a single teacher
        if teacher_val:
            teacher = _resolve_teacher(teacher_val)
            if not teacher:
                return Response(
                    {"error": f"Teacher '{teacher_val}' not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            rules = rules.filter(teacher=teacher)

        if not rules.exists():
            return Response(
                {"error": "No active compensation rules found for this school."},
                status=status.HTTP_404_NOT_FOUND,
            )

        generated_invoices = []

        with transaction.atomic():
            for rule in rules:
                # Check if invoice already exists
                existing = TeacherInvoice.objects.filter(
                    teacher=rule.teacher,
                    school=school,
                    month=month,
                    year=year,
                ).first()

                if existing:
                    # Skip if already generated (don't overwrite)
                    generated_invoices.append(existing)
                    continue

                # Get attendance data for the month
                import datetime
                from django.utils import timezone

                attendance = TeacherAttendance.objects.filter(
                    teacher=rule.teacher,
                    school=school,
                    check_in__year=year,
                    check_in__month=month,
                )
                total_hours = attendance.aggregate(
                    total=Sum('total_hours')
                )['total'] or Decimal('0')

                # Count classes taught
                classes_count = TeacherClassAssignment.objects.filter(
                    teacher=rule.teacher,
                    school=school,
                ).count()

                # Calculate amounts
                base_salary = rule.base_rate
                commission_rate = rule.commission_percentage
                commission_amount = base_salary * commission_rate / Decimal('100')
                adjustments = Decimal('0')
                gross_amount = base_salary + commission_amount + adjustments
                tax_amount = gross_amount * tax_rate / Decimal('100')
                net_amount = gross_amount - tax_amount

                # Generate invoice number
                invoice_number = _generate_invoice_number(year, month)

                invoice = TeacherInvoice.objects.create(
                    invoice_number=invoice_number,
                    teacher=rule.teacher,
                    school=school,
                    month=month,
                    year=year,
                    base_salary=base_salary,
                    total_hours=total_hours,
                    total_classes=classes_count,
                    commission_rate=commission_rate,
                    commission_amount=commission_amount,
                    tax_rate=tax_rate,
                    tax_amount=tax_amount,
                    adjustments=adjustments,
                    gross_amount=gross_amount,
                    net_amount=net_amount,
                    status=InvoiceStatus.DRAFT,
                    generated_by=request.user,
                )
                generated_invoices.append(invoice)

        # Serialize response
        from kms.serializers import TeacherInvoiceSerializer
        serializer = TeacherInvoiceSerializer(generated_invoices, many=True)

        return Response({
            "message": f"Successfully generated {len(generated_invoices)} invoice(s).",
            "invoices": serializer.data,
        }, status=status.HTTP_201_CREATED)


# ==========================================================================
# TEACHER INVOICE MANAGEMENT (LIST / DETAIL / UPDATE)
# ==========================================================================

class TeacherInvoiceManagementView(APIView):
    """
    GET:  List invoices (filterable) or get single invoice detail
    PUT:  Update invoice status, adjustments, notes
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, invoice_id=None):
        from kms.serializers import TeacherInvoiceSerializer

        if invoice_id:
            try:
                invoice = TeacherInvoice.objects.get(id=invoice_id)
                return Response(TeacherInvoiceSerializer(invoice).data)
            except TeacherInvoice.DoesNotExist:
                return Response(
                    {"error": "Invoice not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # List with filters
        queryset = TeacherInvoice.objects.all()

        school = request.query_params.get('school')
        if school:
            resolved = _resolve_school(school)
            if resolved:
                queryset = queryset.filter(school=resolved)

        teacher = request.query_params.get('teacher')
        if teacher:
            resolved = _resolve_teacher(teacher)
            if resolved:
                queryset = queryset.filter(teacher=resolved)

        month = request.query_params.get('month')
        if month:
            queryset = queryset.filter(month=int(month))

        year = request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=int(year))

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        serializer = TeacherInvoiceSerializer(queryset, many=True)
        return Response(serializer.data)

    def put(self, request, invoice_id=None):
        from kms.serializers import TeacherInvoiceSerializer

        if not invoice_id:
            return Response(
                {"error": "Invoice ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            invoice = TeacherInvoice.objects.get(id=invoice_id)
        except TeacherInvoice.DoesNotExist:
            return Response(
                {"error": "Invoice not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update allowed fields
        new_status = request.data.get('status')
        if new_status:
            new_status = new_status.upper()
            valid_statuses = [s.value for s in InvoiceStatus]
            if new_status not in valid_statuses:
                return Response(
                    {"error": f"Invalid status. Must be one of: {valid_statuses}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            invoice.status = new_status

        adjustments = request.data.get('adjustments')
        if adjustments is not None:
            invoice.adjustments = Decimal(str(adjustments))
            # Recalculate totals
            invoice.gross_amount = invoice.base_salary + invoice.commission_amount + invoice.adjustments
            invoice.tax_amount = invoice.gross_amount * invoice.tax_rate / Decimal('100')
            invoice.net_amount = invoice.gross_amount - invoice.tax_amount

        notes = request.data.get('notes')
        if notes is not None:
            invoice.notes = notes

        tax_rate = request.data.get('tax_rate')
        if tax_rate is not None:
            invoice.tax_rate = Decimal(str(tax_rate))
            # Recalculate
            invoice.tax_amount = invoice.gross_amount * invoice.tax_rate / Decimal('100')
            invoice.net_amount = invoice.gross_amount - invoice.tax_amount

        invoice.save()

        return Response(TeacherInvoiceSerializer(invoice).data)
