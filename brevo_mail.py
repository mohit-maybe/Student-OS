import os
from threading import Thread
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Set these in Render's Environment tab:
#   BREVO_API_KEY   -> your Brevo API key (starts with xkeysib-...)
#   SENDER_EMAIL    -> the email address you verified in Brevo
#   SENDER_NAME     -> display name shown to recipients (optional, has a default)

def send_email(to_email, subject, body_text):
    """
    Sends an email via Brevo's HTTP API instead of raw SMTP.
    Returns True on success, raises an Exception on failure
    (so existing try/except blocks in admissions.py keep working unchanged).
    """
    api_key = os.getenv('BREVO_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL')
    sender_name = os.getenv('SENDER_NAME', 'Student OS')

    if not api_key or not sender_email:
        raise Exception("BREVO_API_KEY or SENDER_EMAIL not set in environment variables")

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": sender_email, "name": sender_name},
        subject=subject,
        text_content=body_text
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        raise Exception(f"Brevo API error: {e}")


def send_email_async(to_email, subject, body_text):
    """Fire-and-forget version of send_email: runs the API call in a
    background thread so the request handling the form submission doesn't
    have to wait on the HTTP round-trip to Brevo before responding.
    Failures are logged, not raised, since there's no request left to
    surface them to by the time the thread runs.
    """
    def _send():
        try:
            send_email(to_email, subject, body_text)
        except Exception as e:
            print(f"[Async Brevo Mail] Failed to send '{subject}' to {to_email}: {e}")

    Thread(target=_send, daemon=True).start()
