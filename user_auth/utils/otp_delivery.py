# user_auth/utils/otp_delivery.py

from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings

def send_otp(user, message):
    phone = user.phone_number
    email = user.email

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Try WhatsApp
    try:
        client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{phone}"
        )
        print("OTP sent via WhatsApp ✅")
        return
    except Exception as e:
        print(f"[WhatsApp failed] {e}")

    # Try SMS
    try:
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        print("OTP sent via SMS ✅")
        return
    except Exception as e:
        print(f"[SMS failed] {e}")

    # Fallback: Email
    try:
        send_mail('OTP Verification', message, settings.EMAIL_HOST_USER, [email])
        print("OTP sent via Email ✅")
    except Exception as e:
        print(f"[Email failed] {e}")
