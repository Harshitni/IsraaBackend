import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator


class AuthUsers(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
 
    aud = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    email_confirmed_at = models.DateTimeField(null=True, blank=True)
 
    invited_at = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.CharField(max_length=255, null=True, blank=True)
    confirmation_sent_at = models.DateTimeField(null=True, blank=True)
    recovery_token = models.CharField(max_length=255, null=True, blank=True)
    recovery_sent_at = models.DateTimeField(null=True, blank=True)
 
    email_change_token_new = models.CharField(max_length=255, null=True, blank=True)
    email_change = models.CharField(max_length=255, null=True, blank=True)
    email_change_sent_at = models.DateTimeField(null=True, blank=True)
 
    last_sign_in_at = models.DateTimeField(null=True, blank=True)
    raw_app_meta_data = models.JSONField(null=True, blank=True)
    raw_user_meta_data = models.JSONField(null=True, blank=True)
    is_super_admin = models.BooleanField(null=True, blank=True)
 
    phone = models.CharField(max_length=20, null=True, blank=True)
    phone_confirmed_at = models.DateTimeField(null=True, blank=True)
    phone_change = models.TextField(null=True, blank=True)
    phone_change_token = models.CharField(max_length=255, null=True, blank=True)
    phone_change_sent_at = models.DateTimeField(null=True, blank=True)
 
    email_change_token_current = models.CharField(max_length=255, null=True, blank=True)
    email_change_confirm_status = models.SmallIntegerField(
        null=True, blank=True, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )
    banned_until = models.DateTimeField(null=True, blank=True)
    reauthentication_token = models.CharField(max_length=255, null=True, blank=True)
    reauthentication_sent_at = models.DateTimeField(null=True, blank=True)
    is_sso_user = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
 
    class Meta:
        managed = True
        constraints = [
            models.CheckConstraint(
                check=models.Q(email_change_confirm_status__gte=0) & models.Q(email_change_confirm_status__lte=2),
                name='users_email_change_confirm_status_check'
            ),
        ]
        indexes = [
            models.Index(fields=['id'], name='users_instance_id_idx'),
            models.Index(fields=['is_sso_user'], name='users_is_sso_user_idx'),
        ]
 
    def __str__(self):
        return f"Auth.User(id={self.id}, role={self.role}, is_super_admin={self.is_super_admin})"

