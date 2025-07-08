import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator


class AuthUsers(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User_model')
    id = models.UUIDField(primary_key=True)
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
    email_change_confirm_status = models.SmallIntegerField(null=True, blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    banned_until = models.DateTimeField(null=True, blank=True)
    reauthentication_token = models.CharField(max_length=255, null=True, blank=True)
    reauthentication_sent_at = models.DateTimeField(null=True, blank=True)
    is_sso_user = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # handle = models.TextField()
    
    class Meta:
        managed = True
        constraints = [
            models.CheckConstraint(check=models.Q(email_change_confirm_status__gte=0) & models.Q(email_change_confirm_status__lte=2), name='users_email_change_confirm_status_check'),
        ]
        indexes = [
            models.Index(fields=['id'], name='users_instance_id_idx'),
            models.Index(fields=['is_sso_user'], name='users_is_sso_user_idx'),
        ]

    def __str__(self):
        return f"Auth.User(id={self.id}, role={self.role}, is_super_admin={self.is_super_admin})"


# class AuditLogEntry(models.Model):
#     instance_id = models.UUIDField(null=True, blank=True, db_index=True)
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     payload = models.JSONField(null=True, blank=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     ip_address = models.CharField(max_length=64, default='')

#     class Meta:
#         db_table = 'auth.audit_log_entries'
#         indexes = [
#             models.Index(fields=['instance_id'], name='audit_logs_instance_id_idx'),
#         ]
#         managed = True

#     def __str__(self):
#         return f"Auth.AuditLogEntry(id={self.id}, instance_id={self.instance_id}, created_at={self.created_at})"
    

# class FlowState(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_id = models.UUIDField(null=True, blank=True)
#     auth_code = models.TextField()
#     code_challenge_method = models.CharField(max_length=100)
#     code_challenge = models.TextField()
#     provider_type = models.TextField()
#     provider_access_token = models.TextField(null=True, blank=True)
#     provider_refresh_token = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)
#     authentication_method = models.TextField()
#     auth_code_issued_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.flow_state'
#         managed = True
#         indexes = [
#             models.Index(fields=['auth_code'], name='idx_auth_code'),
#             models.Index(fields=['user_id', 'authentication_method'], name='idx_user_id_auth_method'),
#             models.Index(fields=['-created_at'], name='flow_state_created_at_idx'),
#         ]

#     def __str__(self):
#         return f"Auth.FlowState(id={self.id}, user_id={self.user_id}, auth_code={self.auth_code}, created_at={self.created_at})"
    

# class Identity(models.Model):
#     identities_user_id_fkey = models.ForeignKey('AuthUsers', on_delete=models.CASCADE, related_name='identities')
#     provider_id = models.TextField()
#     user_id = models.UUIDField()
#     identity_data = models.JSONField()
#     provider = models.TextField()
#     last_sign_in_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)
#     email = models.TextField(null=True, editable=False)
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     class Meta:
#         db_table = 'auth.identities'
#         managed = True
#         constraints = [
#             models.UniqueConstraint(fields=['provider_id', 'provider'], name='identities_provider_id_provider_unique'),
#         ]
#         indexes = [
#             models.Index(fields=['user_id'], name='identities_user_id_idx'),
#             models.Index(fields=['email'], name='identities_email_idx'),
#         ]

#     def __str__(self):
#         return f"Auth.Identity(id={self.id}, user_id={self.user_id}, provider={self.provider})"
    

# class Instance(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     uuid = models.UUIDField(null=True, blank=True)
#     raw_base_config = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.instances'
#         managed = True

#     def __str__(self):
#         return f"Auth.Instance(id={self.id}, uuid={self.uuid}, created_at={self.created_at})"
    

# class MfaAmrClaim(models.Model):
#     mfa_amr_claims_session_id_fkey = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='mfa_amr_claims')
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     session_id = models.UUIDField()
#     authentication_method = models.TextField()
#     created_at = models.DateTimeField()
#     updated_at = models.DateTimeField()

#     class Meta:
#         db_table = 'auth.mfa_amr_claims'
#         managed = True
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['session_id', 'authentication_method'],
#                 name='mfa_amr_claims_session_id_authentication_method_pkey'
#             ),
#         ]

#     def __str__(self):
#         return f"Auth.MfaAmrClaim(id={self.id}, session_id={self.session_id}, authentication_method={self.authentication_method})"
    

# class MfaChallenge(models.Model):
#     mfa_challenges_auth_factor_id_fkey = models.ForeignKey('MfaFactor', on_delete=models.CASCADE, related_name='mfa_challenges')
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     factor_id = models.UUIDField()
#     created_at = models.DateTimeField()
#     verified_at = models.DateTimeField(null=True, blank=True)
#     ip_address = models.GenericIPAddressField()
#     otp_code = models.TextField(null=True, blank=True)
#     web_authn_session_data = models.JSONField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.mfa_challenges'
#         managed = True
#         indexes = [
#             models.Index(fields=['-created_at'], name='mfa_challenge_created_at_idx'),
#         ]

#     def __str__(self):
#         return f"Auth.MfaChallenge(id={self.id}, factor_id={self.factor_id}, created_at={self.created_at})"
    

# class MfaFactor(models.Model):
#     mfa_factors_user_id_fkey = models.ForeignKey('AuthUsers', on_delete=models.CASCADE, related_name='mfa_factors')
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_id = models.UUIDField()
#     friendly_name = models.TextField(null=True, blank=True)
#     factor_type = models.CharField(max_length=50)
#     status = models.CharField(max_length=50)
#     created_at = models.DateTimeField()
#     updated_at = models.DateTimeField()
#     secret = models.TextField(null=True, blank=True)
#     phone = models.TextField(null=True, blank=True)
#     last_challenged_at = models.DateTimeField(null=True, blank=True)
#     web_authn_credential = models.JSONField(null=True, blank=True)
#     web_authn_aaguid = models.UUIDField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.mfa_factors'
#         managed = True

#         constraints = [
#             models.UniqueConstraint(fields=['last_challenged_at'], name='mfa_factors_last_challenged_at_key'),
#             models.UniqueConstraint(fields=['user_id', 'phone'], name='unique_phone_factor_per_user'),
#             models.UniqueConstraint(fields=['friendly_name', 'user_id'], name='mfa_factors_user_friendly_name_unique'),
#         ]

#         indexes = [
#             models.Index(fields=['user_id'], name='mfa_factors_user_id_idx'),
#             models.Index(fields=['user_id', 'created_at'], name='factor_id_created_at_idx'),
#         ]

#     def __str__(self):
#         return f"Auth.MfaFactor(id={self.id}, user_id={self.user_id}, factor_type={self.factor_type}, status={self.status})"


# class OneTimeToken(models.Model):
#     one_time_tokens_user_id_fkey = models.ForeignKey('AuthUsers', on_delete=models.CASCADE, related_name='one_time_tokens')
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_id = models.UUIDField()
#     token_type = models.CharField(max_length=50)
#     token_hash = models.TextField(validators=[MinLengthValidator(1)])
#     relates_to = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=False)
#     updated_at = models.DateTimeField(auto_now_add=False)

#     class Meta:
#         db_table = 'auth.one_time_tokens'
#         managed = True

#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(token_hash__length__gt=0),
#                 name='one_time_tokens_token_hash_check'
#             ),
#             models.UniqueConstraint(
#                 fields=['user_id', 'token_type'],
#                 name='one_time_tokens_user_id_token_type_key'
#             ),
#         ]

#         indexes = [
#             models.Index(fields=['token_hash'], name='one_time_tokens_token_hash_idx'),
#             models.Index(fields=['relates_to'], name='one_time_tokens_relates_to_idx'),
#         ]

#     def __str__(self):
#         return f"Auth.OneTimeToken(id={self.id}, user_id={self.user_id}, token_type={self.token_type})"
    

# class Session(models.Model):
#     session_user_id_fkey = models.ForeignKey('AuthUsers', on_delete=models.CASCADE, related_name='sessions')
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_id = models.UUIDField()
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)
#     factor_id = models.UUIDField(null=True, blank=True)
#     aal = models.CharField(max_length=50, null=True, blank=True)
#     not_after = models.DateTimeField(null=True, blank=True)
#     refreshed_at = models.DateTimeField(null=True, blank=True)
#     user_agent = models.TextField(null=True, blank=True)
#     ip = models.GenericIPAddressField(null=True, blank=True)
#     tag = models.TextField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.sessions'
#         managed = True

#         indexes = [
#             models.Index(fields=['-not_after'], name='sessions_not_after_idx'),
#             models.Index(fields=['user_id', 'created_at'], name='user_id_created_at_idx'),
#             models.Index(fields=['user_id'], name='sessions_user_id_idx'),
#         ]

#     def __str__(self):
#         return f"Auth.Session(id={self.id}, user_id={self.user_id}, created_at={self.created_at}, not_after={self.not_after})"
    

# class RefreshToken(models.Model):
#     refresh_token_session_id_fkey = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='refresh_tokens', null=True, blank=True)
#     id = models.BigAutoField(primary_key=True)
#     instance_id = models.UUIDField(null=True, blank=True)
#     token = models.CharField(max_length=255, null=True, blank=True, unique=True)
#     user_id = models.CharField(max_length=255, null=True, blank=True)
#     revoked = models.BooleanField(null=True, blank=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)
#     parent = models.CharField(max_length=255, null=True, blank=True)
#     session_id = models.UUIDField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.refresh_tokens'
#         managed = True

#         indexes = [
#             models.Index(fields=['instance_id'], name='refresh_tokens_instance_id_idx'),
#             models.Index(fields=['instance_id', 'user_id'], name='refresh_tokens_instance_id_user_id_idx'),
#             models.Index(fields=['parent'], name='refresh_tokens_parent_idx'),
#             models.Index(fields=['session_id', 'revoked'], name='refresh_tokens_session_id_revoked_idx'),
#             models.Index(fields=['-updated_at'], name='refresh_tokens_updated_at_idx'),
#         ]

#     def __str__(self):
#         return f"Auth.RefreshToken(id={self.id}, token={self.token}, created_at={self.created_at})"


# class SAMLProvider(models.Model):
#     saml_providers_sso_provider_id_fkey = models.ForeignKey('SSOProvider', on_delete=models.CASCADE, related_name='saml_providers') 
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     sso_provider_id = models.UUIDField()
#     entity_id = models.TextField(validators=[MinLengthValidator(1)], unique=True)
#     metadata_xml = models.TextField(validators=[MinLengthValidator(1)])
#     metadata_url = models.TextField(null=True, blank=True)
#     attribute_mapping = models.JSONField(null=True, blank=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)
#     name_id_format = models.TextField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.saml_providers'
#         managed = True

#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(entity_id__length__gt=0),
#                 name='entity_id_not_empty'
#             ),
#             models.CheckConstraint(
#                 check=(
#                     models.Q(metadata_url__isnull=True) |
#                     models.Q(metadata_url__length__gt=0)
#                 ),
#                 name='metadata_url_not_empty'
#             ),
#             models.CheckConstraint(
#                 check=models.Q(metadata_xml__length__gt=0),
#                 name='metadata_xml_not_empty'
#             ),
#         ]

#         indexes = [
#             models.Index(fields=['sso_provider_id'], name='saml_providers_sso_provider_id_idx'),
#         ]

#     def __str__(self):
#         return f"Auth.SAMLProvider(id={self.id}, sso_provider_id={self.sso_provider_id}, entity_id={self.entity_id})"
    

# class SAMLRelayState(models.Model):
#     saml_relay_states_flow_state_id_fkey = models.ForeignKey('FlowState', on_delete=models.CASCADE, related_name='saml_relay_states', null=True, blank=True)
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     sso_provider_id = models.UUIDField()
#     request_id = models.TextField(validators=[MinLengthValidator(1)])
#     for_email = models.TextField(null=True, blank=True)
#     redirect_to = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)
#     flow_state_id = models.UUIDField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.saml_relay_states'
#         managed = True

#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(request_id__length__gt=0),
#                 name='request_id_not_empty'
#             )
#         ]

#         indexes = [
#             models.Index(fields=['-created_at'], name='saml_relay_states_created_at_idx'),
#             models.Index(fields=['sso_provider_id'], name='saml_relay_states_sso_provider_id_idx'),
#             models.Index(fields=['for_email'], name='saml_relay_states_for_email_idx'),
#         ]

#     def __str__(self):
#         return f"SAMLRelayState(id={self.id}, request_id={self.request_id})"


# class SchemaMigration(models.Model):
#     version = models.CharField(max_length=255, primary_key=True)

#     class Meta:
#         db_table = 'auth.schema_migrations'
#         managed = True

#     def __str__(self):
#         return f"Auth.SchemaMigration(version={self.version})"


# class SSODomain(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     sso_provider_id = models.UUIDField()
#     domain = models.TextField(validators=[MinLengthValidator(1)])
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.sso_domains'
#         managed = True

#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(domain__length__gt=0),
#                 name='domain_not_empty'
#             )
#         ]

#         indexes = [
#             models.Index(fields=['sso_provider_id'], name='sso_domains_sso_provider_id_idx')
#         ]

#     def __str__(self):
#         return f"Auth.SSODomain(id={self.id}, sso_provider_id={self.sso_provider_id}, domain={self.domain})"


# class SSOProvider(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     resource_id = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         db_table = 'auth.sso_providers'
#         managed = True

#         constraints = [
#             models.CheckConstraint(
#                 check=(
#                     models.Q(resource_id__isnull=True) |
#                     models.Q(resource_id__length__gt=0)
#                 ),
#                 name='resource_id_not_empty'
#             )
#         ]

#     def __str__(self):
#         return f"Auth.SSOProvider(id={self.id}, resource_id={self.resource_id})"