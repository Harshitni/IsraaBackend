import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator


class AuthUsers(AbstractUser):
    first_name = None
    last_name = None
    is_staff = None
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invited_at = models.DateTimeField(null=True, blank=True)
    recovery_token = models.CharField(max_length=255, null=True, blank=True)
 
    is_sso_user = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
 
    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id'], name='users_instance_id_idx'),
            models.Index(fields=['is_sso_user'], name='users_is_sso_user_idx'),
        ]
 
    def __str__(self):
        return f"Auth.User(id={self.id}, is_admin={self.is_superuser})"
