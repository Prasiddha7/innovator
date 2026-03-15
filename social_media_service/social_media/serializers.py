from rest_framework import serializers
from .models import User, Category, Profile, Post, Comment, Reaction, ChatMessage

class UserSyncSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=150)
    full_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    role = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    follower_usernames = serializers.SerializerMethodField()
    following_usernames = serializers.SerializerMethodField()
    gender = serializers.CharField(max_length=10, required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_null=True)

    def get_follower_usernames(self, obj):
        # Handle case where obj is a dict (during registration sync) or model instance
        if isinstance(obj, dict):
            return [] # New users have no followers
        return list(obj.followers.values_list('username', flat=True))

    def get_following_usernames(self, obj):
        if isinstance(obj, dict):
            return []
        return list(obj.following.values_list('username', flat=True))

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
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    follower_usernames = serializers.SerializerMethodField()
    following_usernames = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'role', 'profile', 
            'followers_count', 'following_count', 'follower_usernames', 'following_usernames'
        ]

    def get_follower_usernames(self, obj):
        return list(obj.followers.values_list('username', flat=True))

    def get_following_usernames(self, obj):
        return list(obj.following.values_list('username', flat=True))

class PostSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    reactions_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    category_names = serializers.StringRelatedField(many=True, source='categories', read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source='categories'
    )
    shared_post_details = serializers.SerializerMethodField()
    reaction_types = serializers.SerializerMethodField() # List of types and their counts
    current_user_reaction = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'username', 'content', 'image', 'category_names', 'category_ids', 
            'shared_post', 'shared_post_details', 'reactions_count', 'reaction_types',
            'current_user_reaction', 'comments_count', 'comments', 'created_at', 'updated_at'
        ]

    def get_reactions_count(self, obj):
        return obj.reactions.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_comments(self, obj):
        # Only return top-level comments. Nesting in serializer handles the rest.
        top_level_comments = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(top_level_comments, many=True, context=self.context).data

    def get_reaction_types(self, obj):
        from django.db.models import Count
        counts = obj.reactions.values('type').annotate(total=Count('type'))
        return [{"type": item['type'], "count": item['total']} for item in counts]

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
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'username', 'post', 'parent', 'content', 'replies', 'replies_count', 'created_at']
        read_only_fields = ['user']

    def get_replies(self, obj):
        # Limit nesting to prevent huge payloads if needed, or just return all
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_replies_count(self, obj):
        return obj.replies.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('replies_count') == 0:
            representation.pop('replies', None)
            representation.pop('replies_count', None)
        return representation

class CommentReplySerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'username', 'post', 'parent', 'content', 'replies', 'replies_count', 'created_at']
        read_only_fields = ['user', 'post']

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_replies_count(self, obj):
        return obj.replies.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('replies_count') == 0:
            representation.pop('replies', None)
            representation.pop('replies_count', None)
        return representation

    def validate(self, attrs):
        parent = attrs.get('parent')
        if not parent:
            raise serializers.ValidationError({"parent": "Parent comment is required for replies."})
        # Automatically set the post from the parent comment
        attrs['post'] = parent.post
        return attrs

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    receiver_username = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_username', 'receiver_username', 'receiver', 'message', 'is_read', 'created_at']
        read_only_fields = ['sender']
