from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, CustomUser  # adjust imports based on your structure

@receiver(post_save, sender=CustomUser)
def sync_user_to_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            email=instance.email,
            mobile_number=instance.phone_number
        )
    else:
        try:
            profile = instance.profile  # user.profile (from OneToOneField related_name)
            profile.email = instance.email
            profile.mobile_number = instance.phone_number
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(
                user=instance,
                email=instance.email,
                mobile_number=instance.phone_number
            )

# user_auth/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LoginHistory

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Save login history
    LoginHistory.objects.create(user=user)
    # Update counters
    user.update_login_stats()
