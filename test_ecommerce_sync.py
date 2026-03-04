import requests
import uuid

def test_ecommerce_sync():
    unique_user = f"testcustomer_{uuid.uuid4().hex[:6]}"
    payload = {
        "username": unique_user,
        "email": f"{unique_user}@example.com",
        "password": "SecurePassword123!",
        "role": "customer"
    }

    print(f"Registering customer {unique_user}...")
    try:
        response = requests.post("http://localhost:8000/api/accounts/register/", json=payload)
        print("Response from /api/accounts/register/:", response.status_code, response.text)
    except Exception as e:
        print("Error with /api/accounts/register/:", e)

if __name__ == "__main__":
    test_ecommerce_sync()
