import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from custom_auth.models import AuthUsers

class PublicUser(models.Model):
    id = models.BigAutoField(primary_key=False)
    created_at = models.DateTimeField(auto_now_add=False, default=None)
    email = models.TextField(unique=True)
    name = models.TextField()
    user_id = models.TextField(unique=True)
    display_name = models.TextField(null=True, blank=True)
    streak = models.IntegerField(null=True, blank=True, default=0)
    last_active = models.DateTimeField(null=True, blank=True)
    handle = models.TextField(unique=True)

    class Meta:
        db_table = 'public.users'
        managed = False
        unique_together = [('id', 'name')]

        indexes = [
            models.Index(fields=['display_name'], name='idx_users_display_name'),
            models.Index(fields=['user_id'], name='idx_users_user_id'),
            models.Index(fields=['name'], name='idx_users_name'),
            models.Index(fields=['email'], name='idx_users_email'),
        ]

    def __str__(self):
        return f"{self.name} ({self.email})"


class UserProfile(models.Model):
    user_id_fkey = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='profiles')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True)

    name = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    current_emotional_state = models.TextField(null=True, blank=True)
    last_interaction_date = models.DateTimeField(null=True, blank=True)
    notification_preferences = models.JSONField(
        default='{"daily_checkin": true, "weekly_summary": true}', null=True, blank=True
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    is_admin = models.BooleanField(null=True, default=False)
    is_premium = models.BooleanField(null=True, default=False)
    referral_source = models.TextField(null=True, blank=True)
    referral_date = models.DateTimeField(null=True, blank=True)
    subscription_plan = models.TextField(
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
        db_table = 'public.user_profiles'
        managed = False

        constraints = [
            models.UniqueConstraint(fields=['user_id'], name='user_profiles_user_id_key'),
            models.CheckConstraint(
                check=models.Q(
                    subscription_plan__in=[
                        'free', 'monthly', 'yearly', 'family', 'trial'
                    ]
                ),
                name='valid_subscription_plan'
            )
        ]
        indexes = [
            models.Index(fields=['referral_source'], name='idx_user_profiles_referral_source')
        ]

    def __str__(self):
        return f"{self.name or self.email or self.user_id}"


class AccountabilityGroup(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='accountability_groups')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)

    daily_target_pages = models.IntegerField(default=2)
    member_count = models.IntegerField(default=0)
    average_streak = models.IntegerField(default=0)

    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)

    created_by = models.UUIDField(null=True, blank=True)

    invite_code = models.TextField(unique=True)

    group_type = models.CharField(
        max_length=10,
        default='private',
    )

    class Meta:
        db_table = 'public.accountability_groups'
        managed = False

        constraints = [
            models.UniqueConstraint(fields=['invite_code'], name='accountability_groups_invite_code_key')
        ]

    def __str__(self):
        return f"Group(name={self.name}, members={self.member_count}, type={self.group_type})"


class AccountabilityGroupMembership(models.Model):
    group = models.ForeignKey(AccountabilityGroup, on_delete=models.CASCADE, db_column='group_id')
    user = models.ForeignKey(PublicUser, to_field='handle', on_delete=models.CASCADE, db_column='user_handle')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.UUIDField(null=True, blank=True)
    user_handle = models.TextField(null=True, blank=True)

    joined_at = models.DateTimeField(null=False, auto_now_add=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'public.accountability_group_memberships'
        managed = False

        constraints = [
            models.UniqueConstraint(
                fields=['group_id', 'user_handle'],
                name='accountability_group_memberships_group_id_user_handle_key'
            )
        ]

    def __str__(self):
        return f"Membership(user_handle={self.user_handle}, group_id={self.group_id}, admin={self.is_admin})"


class Subscriber(models.Model):
    user_id = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='subscriber')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True)
    email = models.EmailField(unique=True)
    stripe_customer_id = models.TextField(null=True, blank=True)
    subscribed = models.BooleanField(default=False)
    subscription_tier = models.TextField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(null=False)
    created_at = models.DateTimeField(null=False)

    class Meta:
        db_table = 'public.subscribers'
        managed = False

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
    created_at = models.DateTimeField(auto_now_add=False)
    feedback_status = models.TextField(
        null=True,
        blank=True,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ]
    )
    name = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    feedback_phase = models.TextField(
        null=True,
        blank=True,
        choices=[
            ('Under Review', 'Under Review'),
            ('Under Development', 'Under Development'),
            ('Completed', 'Completed'),
        ]
    )

    class Meta:
        db_table = 'public.user_feedbacks'
        managed = False

        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(feedback_phase__in=['Under Review', 'Under Development', 'Completed']) |
                    models.Q(feedback_phase__isnull=True)
                ),
                name='feedback_phase_check'
            ),
            models.CheckConstraint(
                check=models.Q(feedback_status__in=['pending', 'approved', 'rejected']),
                name='user_feedbacks_feedback_status_check'
            )
        ]

    def __str__(self):
        return f"Feedback from {self.email or self.name or 'Unknown'} ({self.feedback_status})"


class UserPrayerSummary(models.Model):
    user_id_fkey = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='prayer_summaries')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    date = models.DateField()
    
    completed_prayers = ArrayField(
        base_field=models.TextField(),
        default=list,
    )

    total_points = models.IntegerField(default=0)

    class Meta:
        db_table = 'public.user_prayer_summary'
        managed = False

        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'date'],
                name='user_prayer_summary_user_id_date_key'
            ),
        ]

    def __str__(self):
        return f"UserPrayerSummary(user_id={self.user_id}, date={self.date})"


class UserPreference(models.Model):
    user_id_fkey = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='preferences')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user_id = models.UUIDField(unique=True)
    
    onboarding_completed = models.BooleanField(null=True, default=False)
    location_privacy_enabled = models.BooleanField(null=True, default=True)
    spiritual_goals = models.JSONField(default=list, null=True, blank=True)
    prayer_reminders = models.BooleanField(null=True, default=True)
    notifications_enabled = models.BooleanField(null=True, default=True)
    daily_quran_goal = models.IntegerField(null=True, default=2)
    
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    
    llm_provider = models.TextField(null=True, default='openai')
    llm_model = models.TextField(null=True, default='gpt-3.5-turbo')
    system_prompt = models.TextField(null=True, blank=True)
    knowledge_base = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'public.user_preferences'
        managed = False

        constraints = [
            models.UniqueConstraint(fields=['user_id'], name='user_preferences_user_id_key'),
        ]

    def __str__(self):
        return f"Preferences(user_id={self.user_id}, llm_model={self.llm_model})"


class UserProfileCommunity(models.Model):
    user_id_fkey = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='profile_community')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True)
    
    display_name = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    spiritual_journey_start = models.DateField(null=True, blank=True)
    is_verified_subscriber = models.BooleanField(null=True, default=False)
    
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'public.user_profiles_community'
        managed = False

        constraints = [
            models.UniqueConstraint(fields=['user_id'], name='user_profiles_community_user_id_key'),
        ]

    def __str__(self):
        return f"CommunityProfile(user_id={self.user_id}, display_name={self.display_name})"


class UserReadingStat(models.Model):
    user_id_fkey = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='user_reading_stats') 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True)

    total_pages_read = models.IntegerField(null=True, default=0)
    current_streak = models.IntegerField(null=True, default=0)
    longest_streak = models.IntegerField(null=True, default=0)
    total_reading_time_seconds = models.IntegerField(null=True, default=0)

    last_reading_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'public.user_reading_stats'
        managed = False

        constraints = [
            models.UniqueConstraint(fields=['user_id'], name='user_reading_stats_user_id_key')
        ]

    def __str__(self):
        return f"UserReadingStat(user_id={self.user_id}, pages={self.total_pages_read})"


class VerseBookmark(models.Model):
    user_id_fkey = models.ForeignKey(AuthUsers, on_delete=models.CASCADE, related_name='verse_bookmarks') 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()

    surah_number = models.IntegerField()
    verse_number = models.IntegerField()
    page_number = models.IntegerField(default=1)

    bookmark_note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'public.verse_bookmarks'
        managed = False

        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'surah_number', 'verse_number', 'page_number'],
                name='verse_bookmarks_user_id_surah_verse_page_unique'
            )
        ]

        indexes = [
            models.Index(fields=['user_id'], name='idx_verse_bookmarks_user_id'),
            models.Index(fields=['surah_number', 'verse_number'], name='idx_verse_bookmarks_surah_verse'),
            models.Index(fields=['page_number'], name='idx_verse_bookmarks_page_number'),
        ]

    def __str__(self):
        return f"Bookmark (User: {self.user_id}, Surah: {self.surah_number}, Ayah: {self.verse_number})"


