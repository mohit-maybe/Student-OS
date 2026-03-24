from flask import Blueprint, request, jsonify, current_app
from extensions import mail, csrf
from flask_mail import Message

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

@webhooks_bp.route('/tally', methods=['POST'])
@csrf.exempt
def tally_webhook():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON payload provided'}), 400

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
                label = field.get('label', '').strip()
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
            
        # 1. Send the internal notification email to the admin
        admin_email = current_app.config.get('MAIL_USERNAME')
        if admin_email:
            try:
                admin_msg = Message(
                    subject=f"New Lead: {school_name} just filled the Onboarding Form!",
                    recipients=[admin_email]
                )
                admin_msg.html = f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2>New School Onboarding Lead</h2>
                    <p>A new school has just submitted the Tally onboarding form. Here are their complete details:</p>
                    <br>
                    {structured_data_html}
                    <br>
                    <p><strong>Note:</strong> We have automatically sent them an email with your Calendly meeting link!</p>
                </div>
                """
                mail.send(admin_msg)
                print(f"[Webhook] Admin notification sent to {admin_email}.")
            except Exception as admin_err:
                print(f"[Webhook] Error sending admin notification: {admin_err}")

        # 2. Send the Calendly email to the school lead
        msg = Message(
            subject="Welcome to Student OS - Let's schedule a discussion!",
            recipients=[email]
        )
        msg.body = f"Hello {contact_name},\n\nThank you for your interest in Student OS for {school_name}!\n\nWe would love to connect with you to discuss how our platform can benefit your institution and answer any questions you might have regarding pricing and features.\n\nPlease schedule a meeting with us at your earliest convenience using the link below:\nhttps://calendly.com/mohitpreets67/discussion-meeting\n\nLooking forward to speaking with you!\n\nBest regards,\nThe Student OS Team"
        
        msg.html = f"""
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
        
        # Send email asynchronously if possible, otherwise synchronously
        mail.send(msg)
        print(f"[Webhook] Email sent to {email} successfully.")
        
        return jsonify({'message': 'Webhook processed and email sent successfully'}), 200

    except Exception as e:
        print(f"[Webhook] Error processing Tally webhook: {e}")
        return jsonify({'error': 'Internal server error processing webhook'}), 500
