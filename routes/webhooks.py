from flask import Blueprint, request, jsonify, current_app
from extensions import mail, csrf
from flask_mail import Message
import requests
import os

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

@webhooks_bp.route('/tally', methods=['POST'])
@csrf.exempt
def tally_webhook():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No JSON payload provided or invalid JSON'}), 400

        # Tally payload has 'data' -> 'fields'
        event_data = data.get('data', {})
        fields = event_data.get('fields', [])
        
        email = None
        school_name = "School Admin"
        contact_name = "there"
        
        # Build a structured HTML table of all submitted fields
        structured_data_html = "<table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%; max-width: 600px; font-family: sans-serif;'>"
        structured_data_html += "<tr style='background-color: #f4f4f5;'><th>Question</th><th>Answer</th></tr>"

        # Safely extract details from Tally fields
        if isinstance(fields, list):
            for field in fields:
                raw_label = field.get('label')
                label = str(raw_label).strip() if raw_label is not None else ''
                value = field.get('value', '')
                
                # Because the structure of the value could theoretically be an array or object, we ensure string conversion for standard fields
                if isinstance(value, list) and len(value) > 0:
                    value = value[0]
                elif not isinstance(value, str):
                    value = str(value)
                    
                # Add to structured HTML
                safe_label = label if label else "Unnamed Field"
                safe_value = value if value else "<i>No response</i>"
                structured_data_html += f"<tr><td style='font-weight: bold; width: 40%;'>{safe_label}</td><td>{safe_value}</td></tr>"
                
                label_lower = label.lower()
                if 'email' in label_lower:
                    email = value
                elif 'school' in label_lower or 'institution' in label_lower:
                    school_name = value
                elif 'name' in label_lower and 'contact' in label_lower:
                    contact_name = value
                elif 'name' in label_lower and contact_name == "there":
                    # Fallback to any generic name field if contact name isn't explicitly defined
                    contact_name = value
                    
        structured_data_html += "</table>"

        if not email:
            print("[Webhook] Processed Tally form but no email address was found in the submission.")
            return jsonify({'message': 'Processed, but no email found'}), 200
            
        print(f"[Webhook] Sending Calendly link to {email} for {school_name}...")
            
        # Send email logic - Fallback to Google Apps Script if SMTP is blocked
        email_api_url = os.environ.get("EMAIL_API_URL", "").strip()
        print(f"[Webhook] EMAIL_API_URL found: {bool(email_api_url)}")
        if email_api_url:
            masked_url = f"{email_api_url[:10]}...{email_api_url[-5:]}" if len(email_api_url) > 15 else "SHORT_URL"
            print(f"[Webhook] Using relay URL: {masked_url}")

        # 1. Send the internal notification email to the admin
        admin_email = current_app.config.get('MAIL_USERNAME')
        admin_subject = f"New Lead: {school_name} just filled the Onboarding Form!"
        admin_html = f"""
        <div style="font-family: Arial, sans-serif; color: #333;">
            <h2>New School Onboarding Lead</h2>
            <p>A new school has just submitted the Tally onboarding form. Here are their complete details:</p>
            <br>
            {structured_data_html}
            <br>
            <p><strong>Note:</strong> We have automatically sent them an email with your Calendly meeting link!</p>
        </div>
        """
        
        if admin_email:
            try:
                if email_api_url:
                    admin_resp = requests.post(email_api_url, json={
                        "to": admin_email,
                        "subject": admin_subject,
                        "htmlBody": admin_html
                    }, timeout=10)
                    print(f"[Webhook] Admin relay response: {admin_resp.status_code} - {admin_resp.text}")
                    if admin_resp.status_code != 200:
                        print(f"[Webhook] Admin relay FAILED: {admin_resp.text}")
                else:
                    admin_msg = Message(subject=admin_subject, recipients=[admin_email])
                    admin_msg.html = admin_html
                    mail.send(admin_msg)
                print(f"[Webhook] Admin notification sent to {admin_email}.")
            except Exception as admin_err:
                print(f"[Webhook] Error sending admin notification: {admin_err}")

        # 2. Send the Calendly email to the school lead
        school_subject = "Welcome to Student OS - Let's schedule a discussion!"
        school_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <p>Hello {contact_name},</p>
            <p>Thank you for your interest in Student OS for <strong>{school_name}</strong>!</p>
            <p>We would love to connect with you to discuss how our platform can benefit your institution and answer any questions you might have regarding pricing and features.</p>
            <p>Please schedule a meeting with us at your earliest convenience using the link below:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="https://calendly.com/mohitpreets67/discussion-meeting" style="display: inline-block; padding: 12px 24px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">Schedule a Meeting</a>
            </p>
            <p>Looking forward to speaking with you!</p>
            <hr style="border: none; border-top: 1px solid #eee; margin-top: 30px;" />
            <p style="font-size: 0.9em; color: #666;">
                Best regards,<br>
                <strong>The Student OS Team</strong>
            </p>
        </div>
        """
        
        if email_api_url:
            print(f"[Webhook] Attempting HTTP POST to relay for {email}...")
            school_resp = requests.post(email_api_url, json={
                "to": email,
                "subject": school_subject,
                "htmlBody": school_html
            }, timeout=15)
            print(f"[Webhook] School relay status: {school_resp.status_code}")
            print(f"[Webhook] School relay response body: {school_resp.text[:200]}")
            if school_resp.status_code != 200:
                print(f"[Webhook] Relay FAILED with status {school_resp.status_code}")
                return jsonify({'error': 'Email relay failed', 'details': school_resp.text}), 502
        else:
            msg = Message(subject=school_subject, recipients=[email])
            msg.body = f"Hello {contact_name},\n\nThank you for your interest in Student OS for {school_name}!\n\nWe would love to connect with you to discuss how our platform can benefit your institution and answer any questions you might have regarding pricing and features.\n\nPlease schedule a meeting with us at your earliest convenience using the link below:\nhttps://calendly.com/mohitpreets67/discussion-meeting\n\nLooking forward to speaking with you!\n\nBest regards,\nThe Student OS Team"
            msg.html = school_html
            mail.send(msg)
            
        print(f"[Webhook] Email sent to {email} successfully.")
        
        return jsonify({'message': 'Webhook processed and email sent successfully'}), 200

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[Webhook] EXCEPTION: {tb}")
        return jsonify({'error': str(e), 'traceback': tb}), 500
