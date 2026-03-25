import json
import urllib.request
import urllib.error

def test_webhook_local():
    url = "http://127.0.0.1:5000/api/webhooks/tally"
    
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
        response = urllib.request.urlopen(req)
        print(f"Status Code: {response.getcode()}")
        print(f"Response: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response data: {e.read().decode('utf-8')}")

if __name__ == "__main__":
    test_webhook_local()
