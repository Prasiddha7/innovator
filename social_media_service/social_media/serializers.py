from rest_framework import serializers
from .models import User, Category, Profile, Post, Comment, Reaction, ChatMessage

class UserSyncSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=150)
    full_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    role = serializers.CharField(max_length=50, required=False, allow_null=True)
    gender = serializers.CharField(max_length=10, required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_null=True)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    interests = CategorySerializer(many=True, read_only=True)
    interest_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source='interests'
    )

    class Meta:
        model = Profile
        fields = ['id', 'username', 'bio', 'avatar', 'interests', 'interest_ids', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'role', 'profile']

class PostSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    reactions_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    category_names = serializers.StringRelatedField(many=True, source='categories', read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source='categories'
    )
    shared_post_details = serializers.SerializerMethodField()
    reaction_counts = serializers.SerializerMethodField()
    current_user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'username', 'content', 'image', 'category_names', 'category_ids', 
            'shared_post', 'shared_post_details', 'reactions_count', 'reaction_counts',
            'current_user_reaction', 'comments_count', 'created_at', 'updated_at'
        ]

    def get_reactions_count(self, obj):
        return obj.reactions.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_reaction_counts(self, obj):
        from django.db.models import Count
        counts = obj.reactions.values('type').annotate(total=Count('type'))
        return {item['type']: item['total'] for item in counts}

    def get_current_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            return reaction.type if reaction else None
        return None

    def get_shared_post_details(self, obj):
        if obj.shared_post:
            return {
                "id": obj.shared_post.id,
                "username": obj.shared_post.user.username,
                "content": obj.shared_post.content,
                "created_at": obj.shared_post.created_at
            }
        return None

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'post', 'type', 'created_at']
        read_only_fields = ['user']

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'username', 'post', 'parent', 'content', 'replies', 'created_at']
        read_only_fields = ['user']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    receiver_username = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_username', 'receiver_username', 'receiver', 'message', 'is_read', 'created_at']
        read_only_fields = ['sender']
