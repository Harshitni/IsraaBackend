import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from datetime import timedelta
from custom_auth.models import AuthUsers

STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

REACTION_CHOICES = [
        ('like', 'Like'),
        ('heart', 'Heart'),
    ]

# class PublicUser(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     created_at = models.DateTimeField(auto_now_add=False, default=None)
#     email = models.TextField(unique=True)
#     name = models.TextField()
#     user_id = models.TextField(unique=True)
#     display_name = models.TextField(null=True, blank=True)
#     streak = models.IntegerField(null=True, blank=True, default=0)
#     last_active = models.DateTimeField(null=True, blank=True)
#     handle = models.TextField(unique=True)

#     class Meta:
#         db_table = 'public.users'
#         managed = True
#         unique_together = [('id', 'name')]
#         indexes = [
#             models.Index(fields=['display_name'], name='idx_users_display_name'),
#             models.Index(fields=['user_id'], name='idx_users_user_id'),
#             models.Index(fields=['name'], name='idx_users_name'),
#             models.Index(fields=['email'], name='idx_users_email'),
#         ]

#     def __str__(self):
#         return f"{self.name} ({self.email})"


class UserProfile(models.Model):
    user_id_fkey = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='profiles')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True)

    name = models.CharField(max_length=255, null=True, blank=True)  #CharField for SQL Server
    email = models.CharField(max_length=255, null=True, blank=True)  #CharField for indexing

    current_emotional_state = models.TextField(null=True, blank=True)
    last_interaction_date = models.DateTimeField(null=True, blank=True)

    notification_preferences = models.JSONField(default=dict, null=True, blank=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    is_admin = models.BooleanField(null=True, default=False)
    is_premium = models.BooleanField(null=True, default=False)

    referral_source = models.CharField(max_length=255, null=True, blank=True)  #CharField for indexing
    referral_date = models.DateTimeField(null=True, blank=True)

    subscription_plan = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        default='free',
        choices=[
            ('free', 'Free'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('family', 'Family'),
            ('trial', 'Trial'),
        ]
    )

    class Meta:
        db_table = 'user_profiles'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user_id'], name='user_profiles_user_id_key'),
            models.CheckConstraint(
                check=models.Q(subscription_plan__in=['free', 'monthly', 'yearly', 'family', 'trial']),
                name='valid_subscription_plan'
            )
        ]
        indexes = [
            models.Index(fields=['referral_source'], name='idx_user_pf_rf_src')
        ]

    def __str__(self):
        return f"{self.name or self.email or self.user_id}"


class AccountabilityGroup(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)  # Use CharField instead of TextField for indexing or constraints
    description = models.TextField(null=True, blank=True)
    daily_target_pages = models.IntegerField(default=2)
    member_count = models.IntegerField(default=0)
    average_streak = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.UUIDField(null=True, blank=True)
    invite_code = models.CharField(max_length=15, unique=True)
    group_type = models.CharField(max_length=10, default='private')

    class Meta:
        db_table = 'accountability_groups'
        managed = True

    def __str__(self):
        return f"Group(name={self.name}, members={self.member_count}, type={self.group_type})"



# # class AccountabilityGroupMembership(models.Model):
# #     group = models.ForeignKey(AccountabilityGroup, on_delete=models.CASCADE)
# #     user = models.ForeignKey(AuthUsers, to_field='handle', on_delete=models.CASCADE)
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# #     acc_group_id = models.UUIDField(null=True, blank=True)
# #     user_handle = models.TextField(null=True, blank=True)
# #     joined_at = models.DateTimeField(null=False, auto_now_add=False)
# #     is_admin = models.BooleanField(default=False)

# #     class Meta:
# #         db_table = 'public.accountability_group_memberships'
# #         managed = True
# #         constraints = [
# #             models.UniqueConstraint(fields=['acc_group_id', 'user_handle'], name='accountability_group_memberships_group_id_user_handle_key')
# #         ]

# #     def __str__(self):
# #         return f"Membership(user_handle={self.user_handle}, acc_group_id={self.acc_group_id}, admin={self.is_admin})"


class Subscriber(models.Model):
    user_fkey = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='subscriber')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True)
    email = models.EmailField(unique=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    subscribed = models.BooleanField(default=False)
    subscription_tier = models.CharField(max_length=50, null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'subscribers'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['email'], name='subscribers_email_key'),
        ]

    def __str__(self):
        return f"Subscriber(email={self.email}, subscribed={self.subscribed})"



class UserFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True)
    feedback_text = models.TextField(default='')
    screenshot_image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    feedback_status = models.CharField(
        max_length=10, null=True, blank=True, default='pending',
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    feedback_phase = models.CharField(
        max_length=25, null=True, blank=True,
        choices=[
            ('Under Review', 'Under Review'),
            ('Under Development', 'Under Development'),
            ('Completed', 'Completed'),
        ]
    )

    class Meta:
        db_table = 'user_feedbacks'
        managed = True
        constraints = [
            models.CheckConstraint(
                check=models.Q(feedback_phase__in=['Under Review', 'Under Development', 'Completed']) |
                      models.Q(feedback_phase__isnull=True),
                name='feedback_phase_check'
            ),
            models.CheckConstraint(
                check=models.Q(feedback_status__in=['pending', 'approved', 'rejected']),
                name='feedback_status_check'
            )
        ]

    def __str__(self):
        return f"Feedback from {self.email or self.name or 'Unknown'} ({self.feedback_status})"



class UserPrayerSummary(models.Model):
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='prayer_summaries')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    completed_prayers = models.JSONField(default=list)
    total_points = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_prayer_summary'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='user_prayer_summary_user_id_date_key'),
        ]

    def __str__(self):
        return f"UserPrayerSummary(user={self.user_id}, date={self.date})"




class UserPreference(models.Model):
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='preferences')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    onboarding_completed = models.BooleanField(null=True, default=False)
    location_privacy_enabled = models.BooleanField(null=True, default=True)
    spiritual_goals = models.JSONField(default=list, null=True, blank=True)
    prayer_reminders = models.BooleanField(null=True, default=True)
    notifications_enabled = models.BooleanField(null=True, default=True)
    daily_quran_goal = models.IntegerField(null=True, default=2)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    llm_provider = models.CharField(max_length=50, null=True, default='openai')
    llm_model = models.CharField(max_length=50, null=True, default='gpt-3.5-turbo')
    system_prompt = models.TextField(null=True, blank=True)
    knowledge_base = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'user_preferences'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user'], name='user_preferences_user_id_key'),
        ]

    def __str__(self):
        return f"Preferences(user={self.user_id}, llm_model={self.llm_model})"




class UserProfileCommunity(models.Model):
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='profile_community')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    spiritual_journey_start = models.DateField(null=True, blank=True)
    is_verified_subscriber = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'user_profiles_community'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user'], name='user_profiles_community_user_id_key'),
        ]

    def __str__(self):
        return f"CommunityProfile(user={self.user_id}, display_name={self.display_name})"




class UserReadingStat(models.Model):
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='user_reading_stats')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_pages_read = models.IntegerField(null=True, default=0)
    current_streak = models.IntegerField(null=True, default=0)
    longest_streak = models.IntegerField(null=True, default=0)
    total_reading_time_seconds = models.IntegerField(null=True, default=0)
    last_reading_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'user_reading_stats'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user'], name='user_reading_stats_user_id_key'),
        ]

    def __str__(self):
        return f"UserReadingStat(user={self.user_id}, pages={self.total_pages_read})"



class VerseBookmark(models.Model):
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='verse_bookmarks')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    surah_number = models.IntegerField()
    verse_number = models.IntegerField()
    page_number = models.IntegerField(default=1)
    bookmark_note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'verse_bookmarks'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user', 'surah_number', 'verse_number', 'page_number'], name='verse_bookmarks_user_id_surah_verse_page_unique')
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_verse_bookmarks_user_id'),
            models.Index(fields=['surah_number', 'verse_number'], name='idx_vs_bmk_sSh_verse'),
            models.Index(fields=['page_number'], name='idx_vs_bk_pg_nbr'),
        ]

    def __str__(self):
        return f"Bookmark (User: {self.user_id}, Surah: {self.surah_number}, Ayah: {self.verse_number})"


class KnowledgeBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id')
    filename = models.TextField()
    content = models.TextField()
    file_type = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'knowledge_base'
        managed = True

    def __str__(self):
        return f"{self.filename} uploaded by {self.user_id}"


class NotificationSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id')
    notification_type = models.TextField()
    scheduled_for = models.DateTimeField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notification_schedule'
        managed = True

    def __str__(self):
        return f"Notification for {self.user_id} at {self.scheduled_for}"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id')
    notification_type = models.TextField()
    title = models.TextField()
    message = models.TextField()
    data = models.TextField(null=True, blank=True, default='{}')
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        managed = True
        indexes = [
            models.Index(fields=['user_id', 'created_at'], name='idx_noti_usr_id_ct_at')
        ]

    def __str__(self):
        return f"Notification({self.title}) to {self.user_id}"


class PalMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = models.UUIDField()
    receiver_id = models.UUIDField()
    connection_id = models.UUIDField()
    message_content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)
    message_type = models.TextField(default='text')

    class Meta:
        db_table = 'pal_messages'
        managed = True
        indexes = [
            models.Index(fields=['connection_id', 'created_at'], name='idx_pal_messages_connection_id'),
            models.Index(fields=['sender_id', 'receiver_id', 'created_at'], name='idx_pal_messages_participants'),
        ]

    def __str__(self):
        return f"Message {self.id} from {self.sender_id} to {self.receiver_id}"


class PrayerPalConnection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester_id = models.UUIDField()
    receiver_id = models.UUIDField()
    status = models.TextField(default='pending')
    connection_type = models.TextField(default='prayer')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'prayer_pal_connections'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['requester_id', 'receiver_id'], name='prayer_pal_connections_requester_id_receiver_id_key'),
            models.CheckConstraint(check=models.Q(status__in=['pending', 'accepted', 'declined']), name='prayer_pal_connections_status_check'),
            models.CheckConstraint(check=models.Q(connection_type__in=['prayer', 'quran']), name='check_connection_type'),
        ]
        indexes = [
            models.Index(fields=['requester_id'], name='idx_prayer_pal_connection_req'),
            models.Index(fields=['receiver_id'], name='idx_prayer_pal_connection_rec'),
        ]

    def __str__(self):
        return f"Connection: {self.requester_id} ➝ {self.receiver_id} ({self.status})"


class PrayerReward(models.Model):
    name = models.CharField(max_length=255, primary_key=True)  # Changed from TextField to CharField
    reward = models.IntegerField()

    class Meta:
        db_table = 'prayer_rewards'
        managed = True

    def __str__(self):
        return f"{self.name}: {self.reward} points"


class PostCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # ✅ Fixed
    description = models.TextField(null=True, blank=True)
    icon_name = models.CharField(max_length=255, null=True, blank=True)  # ✅ Better than TextField
    created_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        db_table = 'post_categories'
        managed = True

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
        db_table = 'community_posts'
        managed = True
        indexes = [
            models.Index(fields=['created_at'], name='idx_community_posts_created_at'),
            models.Index(fields=['is_pinned', 'created_at'], name='idx_community_posts_pinned'),
        ]

    def __str__(self):
        return f"{'Anonymous' if self.is_anonymous else self.user_id} - {self.title[:30]}"

class PrayerSupport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, db_column='post_id', related_name='prayer_supports')
    supporter_user_id = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'prayer_support'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['post_id', 'supporter_user_id'], name='prayer_support_post_id_supporter_user_id_key')
        ]

    def __str__(self):
        return f"Support by {self.supporter_user_id} on post {self.post_id}"


class PushSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.CharField(max_length=500)  # was TextField
    p256dh_key = models.CharField(max_length=255)  # was TextField
    auth_key = models.CharField(max_length=255)  # was TextField
    user_agent = models.CharField(max_length=255, null=True, blank=True)  # was TextField
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'push_subscriptions'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user', 'endpoint'], name='push_subscriptions_user_endpoint_key')
        ]

    def __str__(self):
        return f"PushSubscription(id={self.id}, user={self.user_id})"



class QuranProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='quran_progress')
    surah_number = models.IntegerField()
    page_number = models.IntegerField()
    completed_at = models.DateTimeField(default=timezone.now)
    reading_time_seconds = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    session_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    streak_day = models.IntegerField(null=True, default=1)

    class Meta:
        db_table = 'quran_progress'
        managed = True

    def __str__(self):
        return f"QuranProgress(user={self.user_id}, surah={self.surah_number}, page={self.page_number})"



class SavedPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='saved_posts')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'saved_posts'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'post'], name='saved_posts_user_post_key')
        ]

    def __str__(self):
        return f"SavedPost(user={self.user_id}, post={self.post_id})"


class AdminAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='admin_actions')
    target_user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='target_admin_actions')
    action_type = models.CharField(max_length=100)  # was TextField
    details = models.TextField(default='{}', null=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'admin_actions'
        managed = True

    def __str__(self):
        return f"AdminAction(id={self.id}, type={self.action_type}, by={self.admin_user_id})"



class CacheMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cache_type = models.CharField(max_length=255, unique=True)  # was TextField
    last_updated = models.DateTimeField()
    total_records = models.IntegerField(default=0)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'cache_metadata'
        managed = True
        indexes = [
            models.Index(fields=['cache_type'], name='idx_cache_metadata_type')
        ]

    def __str__(self):
        return f"{self.cache_type} - {self.total_records} records"



class CachedChapters(models.Model):
    id = models.IntegerField(primary_key=True)
    revelation_place = models.CharField(max_length=50)
    revelation_order = models.IntegerField()
    bismillah_pre = models.BooleanField(default=False)
    name_simple = models.CharField(max_length=255)  # was TextField
    name_complex = models.CharField(max_length=255)  # was TextField
    name_arabic = models.CharField(max_length=255)  # was TextField
    verses_count = models.IntegerField()
    pages = models.TextField(default='{}')
    translated_name = models.TextField(default='{}')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'cached_chapters'
        managed = True
        indexes = [
            models.Index(fields=['name_simple'], name='idx_cached_chapters_name')
        ]

    def __str__(self):
        return f"{self.id} - {self.name_simple}"


class CachedReciter(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    style = models.TextField(null=True, default='{}')
    qirat = models.TextField(null=True, default='{}')
    translated_name = models.TextField(null=True, default='{}')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cached_reciters'
        managed = True
        indexes = [
            models.Index(fields=['name'], name='idx_cached_reciters_name')
        ]

    def __str__(self):
        return f"{self.id} - {self.name}"


class ChallengeGroupMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.UUIDField()
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='challenge_group_memberships')
    daily_target_pages = models.IntegerField(default=2)
    joined_at = models.DateTimeField(null=True, auto_now_add=True)
    is_admin = models.BooleanField(null=True, default=False)

    class Meta:
        db_table = 'challenge_group_members'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['group_id', 'user'], name='challenge_group_members_group_user_key')
        ]
        indexes = [
            models.Index(fields=['group_id'], name='idx_clg_grp_mbr_grp'),
            models.Index(fields=['user'], name='idx_clg_grp_mbr_usr')
        ]

    def __str__(self):
        return f"Member {self.user_id} in Group {self.group_id}"



class ChatHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='chat_messages')
    session_id = models.UUIDField(default=uuid.uuid4)
    message_type = models.CharField(max_length=10)  # ✅ Safe for enum values
    message_content = models.TextField(validators=[MinLengthValidator(1)])
    emotion_context = models.TextField(null=True, blank=True)
    interaction_type = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'chat_history'
        managed = True
        constraints = [
            models.CheckConstraint(check=models.Q(message_type__in=['user', 'noor']), name='chat_history_message_type_check')
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_chat_history_user_id'),
            models.Index(fields=['session_id'], name='idx_chat_history_session_id'),
            models.Index(fields=['created_at'], name='idx_chat_history_created_at')
        ]

    def __str__(self):
        return f"{self.message_type.title()} Message (User {self.user_id})"




class CommunityComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, db_column='post_id', related_name='comments')
    user = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, null=True, db_column='user_id', related_name='user_comments')
    user_profile = models.ForeignKey(UserProfileCommunity, to_field='user_id', db_column='user_profile', on_delete=models.CASCADE, related_name='profile_comments')
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'community_comments'
        managed = True
        indexes = [
            models.Index(fields=['post', 'created_at'], name='idx_community_comments_post_id')
        ]

    def __str__(self):
        return f"Comment by {'Anonymous' if self.is_anonymous else self.user_id} on Post {self.post_id}"


class CommunityJoinRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community_id = models.UUIDField()
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='join_requests')
    request_message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(AuthUsers, on_delete=models.SET_NULL, null=True, blank=True, db_column='reviewed_by', related_name='reviewed_requests')

    class Meta:
        db_table = 'community_join_requests'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['community_id', 'user_id'], name='community_join_requests_community_id_user_id_key'),
            models.CheckConstraint(check=models.Q(status__in=['pending', 'approved', 'rejected']), name='community_join_requests_status_check')
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.community_id} [{self.status}]"



class CommunityReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='community_reactions')
    post_id = models.ForeignKey('CommunityPost', on_delete=models.CASCADE, null=True, blank=True, db_column='post_id', related_name='reactions')
    comment_id = models.ForeignKey('CommunityComment', on_delete=models.CASCADE, null=True, blank=True, db_column='comment_id', related_name='reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'community_reactions'
        managed = True
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(post_id__isnull=False, comment_id__isnull=True) |
                    models.Q(post_id__isnull=True, comment_id__isnull=False)
                ),
                name='post_or_comment_check'
            ),
            models.CheckConstraint(
                check=models.Q(reaction_type__in=['like', 'heart']),
                name='community_reactions_reaction_type_check'
            ),
            models.UniqueConstraint(
                fields=['user_id', 'post_id', 'reaction_type'],
                name='unique_user_post_reaction'
            ),
            models.UniqueConstraint(
                fields=['user_id', 'comment_id', 'reaction_type'],
                name='unique_user_comment_reaction'
            ),
        ]
        indexes = [
            models.Index(fields=['post_id'], name='idx_com_rec_pst_id'),
            models.Index(fields=['comment_id'], name='idx_com_rec_cmt_id'),
        ]

    def __str__(self):
        target = "Post" if self.post_id else "Comment"
        return f"{self.user_id} reacted to {target} ({self.reaction_type})"



class DiscountCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
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
        db_table = 'discount_codes'
        managed = True

    def __str__(self):
        return f"{self.code} ({self.discount_percentage or self.discount_amount} off)"


class DuaFavorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='user_id', related_name='dua_favorites')
    dua_category = models.CharField(max_length=100)
    dua_id = models.IntegerField()
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'dua_favorites'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'dua_category', 'dua_id'], name='dua_favorites_user_id_dua_category_dua_id_key')
        ]
        indexes = [
            models.Index(fields=['user_id', 'dua_category'], name='idx_dua_fvt_usr_cat')
        ]

    def __str__(self):
        return f"Favorite Dua {self.dua_id} in {self.dua_category} by user {self.user_id}"


class EmotionalTracking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    emotion_type = models.CharField(max_length=50)
    intensity_level = models.IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(100)])
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, default=timezone.now)

    class Meta:
        db_table = 'emotional_tracking'
        managed = True
        indexes = [
            models.Index(fields=['user_id'], name='idx_eml_trk_usr_id'),
            models.Index(fields=['created_at'], name='idx_eml_trk_ctd_at')
        ]

    def __str__(self):
        return f"{self.user_id} - {self.emotion_type} ({self.intensity_level})"



class FreeTrial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='free_trial')
    activated_by = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='activated_trial')
    activated_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(days=7))
    is_active = models.BooleanField(null=True, default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'free_trials'
        managed = True

    def __str__(self):
        return f"FreeTrial(user_id={self.user_id}, active={self.is_active})"


class GroupChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.ForeignKey(AccountabilityGroup, on_delete=models.CASCADE, db_column='group_id', related_name='group_chat_messages')
    user_id = models.UUIDField()
    message_content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    replied_to_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='replied_to_message_id', related_name='replies')
    reply_preview = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'group_chat_messages'
        managed = True
        indexes = [
            models.Index(fields=['replied_to_message'], name='idx_gp_chat_msg_rp_to'),
        ]

    def __str__(self):
        return f"{self.user_id}: {self.message_content[:30]}..."
    

class GroupChatParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.ForeignKey(AccountabilityGroup, on_delete=models.CASCADE, db_column='group_id', related_name='participants')
    user_id = models.UUIDField()
    joined_at = models.DateTimeField(auto_now_add=False, default=None, null=True, blank=True)

    class Meta:
        db_table = 'group_chat_participants'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['group_id', 'user_id'], name='group_chat_participants_group_id_user_id_key')
        ]

    def __str__(self):
        return f"GroupChatParticipant(user_id={self.user_id}, group_id={self.group_id})"


class GroupJoinRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.ForeignKey(AccountabilityGroup, on_delete=models.CASCADE, db_column='group_id', related_name='group_join_requests')
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name="group_joining_user")
    invite_code = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=False, default=None, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(AuthUsers, on_delete=models.SET_NULL, db_column='reviewed_by', null=True, blank=True, related_name='reviewed_group_requests')

    class Meta:
        db_table = 'group_join_requests'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['group_id', 'user_id'], name='group_join_requests_group_id_user_id_key'),
            models.CheckConstraint(check=models.Q(status__in=['pending', 'approved', 'rejected']), name='group_join_requests_status_check'),
        ]

    def __str__(self):
        return f"JoinRequest(user_id={self.user_id}, group={self.group_id}, status={self.status})"


class InteractionHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    activity_type = models.TextField()
    activity_id = models.TextField(null=True, blank=True)
    action = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    recent_activity = models.TextField(default='{}', null=True)

    class Meta:
        db_table = 'interaction_history'
        managed = True

    def __str__(self):
        return f"InteractionHistory(user={self.user_id}, activity_type={self.activity_type})"


class InvitationCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20)
    created_by = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, db_column='created_by')
    discount_percentage = models.IntegerField(null=True, default=50)
    usage_limit = models.IntegerField(null=True, default=10)
    usage_count = models.IntegerField(null=True, default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(null=True, default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'invitation_codes'
        managed = True

    def __str__(self):
        return f"InvitationCode(code={self.code}, active={self.is_active})"
    

class PlatformAIConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.TextField(default='openai')
    model = models.TextField(default='gpt-4-turbo')
    system_prompt = models.TextField(null=True, blank=True)
    knowledge_base = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = 'platform_ai_config'
        managed = True

    def __str__(self):
        return f"{self.provider} - {self.model} (Active: {self.is_active})"
