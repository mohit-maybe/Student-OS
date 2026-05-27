import json
import urllib.request
import urllib.error

def test_webhook_live():
    # Make a request to the live Render website
    url = "https://student-os.onrender.com/api/webhooks/tally"
    
    tally_mock_payload = {
        "eventId": "test_event",
        "eventType": "FORM_RESPONSE",
        "data": {
            "fields": [
                {
                    "label": "School Name?",
                    "value": "Test Live School"
                },
                {
                    "label": "Email Address?",
                    "value": "mohitpreets67@gmail.com"
                },
                {
                    "label": "Contact Person Name?",
                    "value": "Admin User"
                },
                {
                    "label": "Board (CBSE / ICSE / State / International)?",
                    "value": "CBSE"
                }
            ]
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(tally_mock_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        print(f"Sending webhook to {url} ...")
        response = urllib.request.urlopen(req)
        print(f"Status Code: {response.status_code if hasattr(response, 'status_code') else response.getcode()}")
        print(f"Response: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response data: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_webhook_live()
