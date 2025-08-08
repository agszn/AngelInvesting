from twilio.rest import Client
import re

def normalize_phone_number(phone_number):
    phone_number = phone_number.strip()
    phone_number = re.sub(r'\D', '', phone_number)
    if phone_number.startswith('91') and len(phone_number) == 12:
        return f"+{phone_number}"
    elif len(phone_number) == 10 and phone_number[0] in '6789':
        return f"+91{phone_number}"
    elif phone_number.startswith('+91') and len(phone_number) == 13:
        return phone_number
    return None

def send_otp(user, message):
    from django.conf import settings
    from twilio.base.exceptions import TwilioRestException

    phone = normalize_phone_number(user.phone_number)
    if not phone:
        print("Invalid phone number format.")
        return

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        # Send via SMS
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
    except TwilioRestException as e:
        print("SMS sending failed:", e)
        # Optional: try WhatsApp as fallback
        try:
            client.messages.create(
                body=message,
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to="whatsapp:" + phone
            )
        except TwilioRestException as we:
            print("WhatsApp sending failed:", we)
