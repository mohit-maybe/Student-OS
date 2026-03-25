from app import app

def test_homepage():
    test_client = app.test_client()
    with app.app_context():
        print("Sending GET / ...")
        response = test_client.get('/')
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Error data snippet:", response.data[:500])
        else:
            print("Successfully loaded homepage.")

if __name__ == "__main__":
    test_homepage()
