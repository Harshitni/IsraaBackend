import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from custom_auth.models import AuthUsers
from public.models import UserProfileCommunity


class AdminAction(models.Model):
    admin_user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='admin_actions')
    target_user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='target_admin_actions')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user_id = models.UUIDField()
    action_type = models.TextField()
    details = models.TextField(default='{}', null=True)
    created_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        db_table = 'public.admin_actions'
        managed = False

    def __str__(self):
        return f"AdminAction(id={self.id}, type={self.action_type}, by={self.admin_user_id})"


class CacheMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cache_type = models.TextField(unique=True)
    last_updated = models.DateTimeField(auto_now_add=False)
    total_records = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        db_table = 'public.cache_metadata'
        managed = False
        indexes = [
            models.Index(fields=['cache_type'], name='idx_cache_metadata_type'),
        ]

    def __str__(self):
        return f"{self.cache_type} - {self.total_records} records"


class CachedChapters(models.Model):
    id = models.IntegerField(primary_key=True)
    revelation_place = models.TextField()
    revelation_order = models.IntegerField()
    bismillah_pre = models.BooleanField(default=False)
    name_simple = models.TextField()
    name_complex = models.TextField()
    name_arabic = models.TextField()
    verses_count = models.IntegerField()
    pages = models.TextField(default='{}')
    translated_name = models.TextField(default='{}')
    created_at = models.DateTimeField(auto_now_add=False)
    updated_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        db_table = 'public.cached_chapters'
        managed = False
        indexes = [
            models.Index(fields=['name_simple'], name='idx_cached_chapters_name'),
        ]

    def __str__(self):
        return f"{self.id} - {self.name_simple}"


class CachedReciter(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    style = models.TextField(null=True, default='{}')
    qirat = models.TextField(null=True, default='{}')
    translated_name = models.TextField(null=True, default='{}')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'public.cached_reciters'
        managed = False
        indexes = [
            models.Index(fields=['name'], name='idx_cached_reciters_name'),
        ]

    def __str__(self):
        return f"{self.id} - {self.name}"


class ChallengeGroupMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.UUIDField()
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='challenge_group_memberships')
    daily_target_pages = models.IntegerField(default=2)
    joined_at = models.DateTimeField(null=True, auto_now_add=True)
    is_admin = models.BooleanField(null=True, default=False)

    class Meta:
        db_table = 'public.challenge_group_members'
        managed = False
        constraints = [
            models.UniqueConstraint(fields=['group_id', 'user_id'], name='challenge_group_members_group_id_user_id_key'),
        ]
        indexes = [
            models.Index(fields=['group_id'], name='idx_challenge_group_members_group'),
            models.Index(fields=['user_id'], name='idx_challenge_group_members_user'),
        ]

    def __str__(self):
        return f"Member {self.user_id} in Group {self.group_id}"


class ChatHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='chat_messages')    
    session_id = models.UUIDField(default=uuid.uuid4)
    message_type = models.CharField(max_length=10)  # Only 'user' or 'noor' allowed
    message_content = models.TextField(validators=[MinLengthValidator(1)])
    emotion_context = models.TextField(null=True, blank=True)
    interaction_type = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        db_table = 'public.chat_history'
        managed = False
        constraints = [
            models.CheckConstraint(check=models.Q(message_type__in=['user', 'noor']), name='chat_history_message_type_check'),
        ]
        indexes = [
            models.Index(fields=['user_id'], name='idx_chat_history_user_id'),
            models.Index(fields=['session_id'], name='idx_chat_history_session_id'),
            models.Index(fields=['created_at'], name='idx_chat_history_created_at'),
        ]

    def __str__(self):
        return f"{self.message_type.title()} Message (User {self.user_id})"


class PostCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    icon_name = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        db_table = 'public.post_categories'
        managed = False

    def __str__(self):
        return self.name


class CommunityPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, related_name='community_posts', on_delete=models.CASCADE, null=True)
    community_profile_id = models.ForeignKey(UserProfileCommunity, on_delete=models.CASCADE, null=True, related_name='profile_posts')
    category_id = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    title = models.TextField()
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=False)
    updated_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        db_table = 'public.community_posts'
        managed = False
        indexes = [
            models.Index(fields=['created_at'], name='idx_community_posts_created_at'),
            models.Index(fields=['is_pinned', 'created_at'], name='idx_community_posts_pinned'),
        ]

    def __str__(self):
        return f"{'Anonymous' if self.is_anonymous else self.user_id} - {self.title[:30]}"


class CommunityComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, db_column='post_id', related_name='comments')
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, null=True, db_column='user_id', related_name='user_comments')
    user_profile = models.ForeignKey(UserProfileCommunity, to_field='user_id', db_column='user_id', on_delete=models.CASCADE, related_name='profile_comments')
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=False)
    updated_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        db_table = 'public.community_comments'
        managed = False
        indexes = [
            models.Index(fields=['post_id', 'created_at'], name='idx_community_comments_post_id'),
        ]

    def __str__(self):
        return f"Comment by {'Anonymous' if self.is_anonymous else self.user_id} on Post {self.post_id}"

STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

class CommunityJoinRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community_id = models.UUIDField()
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='join_requests')
    request_message = models.TextField(null=True, blank=True)
    status = models.TextField(choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(AuthUsers, on_delete=models.SET_NULL, null=True, blank=True, db_column='reviewed_by', related_name='reviewed_requests')

    class Meta:
        db_table = 'public.community_join_requests'
        managed = False
        constraints = [
            models.UniqueConstraint(fields=['community_id', 'user_id'], name='community_join_requests_community_id_user_id_key'),
            models.CheckConstraint(check=models.Q(status__in=['pending', 'approved', 'rejected']), name='community_join_requests_status_check')
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.community_id} [{self.status}]"


REACTION_CHOICES = [
        ('like', 'Like'),
        ('heart', 'Heart'),
    ]

class CommunityReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='community_reactions')
    post_id = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, null=True, blank=True, db_column='post_id', related_name='reactions')
    comment_id = models.ForeignKey(CommunityComment, on_delete=models.CASCADE, null=True, blank=True, db_column='comment_id', related_name='reactions')
    reaction_type = models.TextField(choices=REACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'public.community_reactions'
        managed = False
        constraints = [
            models.CheckConstraint(check=models.Q(post__isnull=False, comment__isnull=True),name='post_or_comment_check'),
            models.CheckConstraint(check=models.Q(reaction_type__in=['like', 'heart']),name='community_reactions_reaction_type_check'),
            models.UniqueConstraint(fields=['user_id', 'post_id', 'reaction_type'], name='unique_user_post_reaction'),
            models.UniqueConstraint(fields=['user_id', 'comment_id', 'reaction_type'], name='unique_user_comment_reaction'),
        ]
        indexes = [
            models.Index(fields=['post_id'], name='idx_community_reactions_post_id'),
            models.Index(fields=['comment_id'], name='idx_community_reactions_comment_id'),
        ]

    def __str__(self):
        target = "Post" if self.post_id else "Comment"
        return f"{self.user_id} reacted to {target} ({self.reaction_type})"


class DiscountCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.TextField(unique=True)
    discount_percentage = models.IntegerField(null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    expiry_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(AuthUsers, on_delete=models.SET_NULL, null=True, db_column='created_by', related_name='discount_codes_created')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'public.discount_codes'
        managed = False

    def __str__(self):
        return f"{self.code} ({self.discount_percentage or self.discount_amount} off)"


class DuaFavorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='dua_favorites')
    dua_category = models.TextField()
    dua_id = models.IntegerField()
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'public.dua_favorites'
        managed = False
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'dua_category', 'dua_id'], name='dua_favorites_user_id_dua_category_dua_id_key')
        ]
        indexes = [
            models.Index(fields=['user', 'dua_category'], name='idx_dua_favorites_user_category')
        ]

    def __str__(self):
        return f"Favorite Dua {self.dua_id} in {self.dua_category} by user {self.user_id}"


class EmotionalTracking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    emotion_type = models.TextField()
    intensity_level = models.IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(100)])
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, default=timezone.now)

    class Meta:
        db_table = 'public.emotional_tracking'
        managed = False
        indexes = [
            models.Index(fields=['user_id'], name='idx_emotional_tracking_user_id'),
            models.Index(fields=['created_at'], name='idx_emotional_tracking_created_at')
        ]

    def __str__(self):
        return f"{self.user_id} - {self.emotion_type} ({self.intensity_level})"


class FreeTrial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='free_trial')
    activated_by = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='activated_trial')
    activated_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=lambda: timezone.now() + timedelta(days=7))
    is_active = models.BooleanField(null=True, default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'public.free_trials'
        managed = False

    def __str__(self):
        return f"FreeTrial(user_id={self.user_id}, active={self.is_active})"
