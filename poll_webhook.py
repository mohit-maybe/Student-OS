import json
import urllib.request
import urllib.error
import time

def poll():
    url = "https://student-os.onrender.com/api/webhooks/tally"
    
    tally_mock_payload = {
        "eventId": "test_event",
        "eventType": "FORM_RESPONSE",
        "data": {
            "fields": [
                {
                    "label": "School Name?",
                    "value": "Test Polling School"
                },
                {
                    "label": "Email Address?",
                    "value": "mohitpreets67@gmail.com"
                },
                {
                    "label": "Contact Person Name?",
                    "value": "Admin Poller"
                }
            ]
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(tally_mock_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    attempts = 0
    while attempts < 30:
        attempts += 1
        try:
            print(f"Attempt {attempts}: Sending webhook to {url} ...")
            response = urllib.request.urlopen(req, timeout=10)
            status = response.getcode()
            body = response.read().decode('utf-8')
            print(f"Status: {status}\nBody: {body}\n")
            if "Webhook processed" in body or status == 200:
                print("SUCCESS! The deploy is live and working.")
                break
        except urllib.error.HTTPError as e:
            status = e.code
            body = e.read().decode('utf-8')
            print(f"HTTP Error: {status}\nBody: {body}\n")
            if "traceback" in body:
                print("Captured backend traceback successfully!")
                break
            else:
                print("Still getting old 500 error or 502 Bad Gateway. Retrying in 15 seconds...")
        except Exception as e:
            print(f"Generic Error: {e}")
        
        time.sleep(15)

if __name__ == "__main__":
    poll()
