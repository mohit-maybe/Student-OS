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
            
        print(f"[Webhook] Successfully logged submission for {school_name} from {email}.")
        return jsonify({'message': 'Webhook received and logged successfully'}), 200

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[Webhook] EXCEPTION: {tb}")
        return jsonify({'error': str(e), 'traceback': tb}), 500
