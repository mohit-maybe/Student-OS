import json
from app import app
from extensions import mail

def test_webhook():
    test_client = app.test_client()
    
    tally_mock_payload = {
        "eventId": "test_event",
        "eventType": "FORM_RESPONSE",
        "data": {
            "fields": [
                {
                    "label": "Name of School",
                    "value": "Test High School"
                },
                {
                    "label": "Contact Person Email",
                    "value": "test@example.com"
                },
                {
                    "label": "Contact Person Name",
                    "value": "John Doe"
                }
            ]
        }
    }
    
    with app.app_context():
        # Prevent actually sending an email by using the test mail context
        with mail.record_messages() as outbox:
            response = test_client.post('/api/webhooks/tally', 
                                     data=json.dumps(tally_mock_payload), 
                                     content_type='application/json')
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Data: {response.json}")
            
            if outbox:
                print(f"Emails sent: {len(outbox)}")
                print(f"To: {outbox[0].recipients}")
                print(f"Subject: {outbox[0].subject}")
                print(f"Body snippet: {outbox[0].body[:50]}")
            else:
                print("No emails were sent.")

if __name__ == "__main__":
    test_webhook()
