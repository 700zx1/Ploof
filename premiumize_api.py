import os
import json
import requests
from PyQt6.QtWidgets import QInputDialog, QMessageBox

CONFIG_FILE = "config.json"
API_BASE = "https://www.premiumize.me/api"

class PremiumizeClient:
    def __init__(self):
        self.token = load_or_prompt_token()
        print(f"Using token: {self.token}")  # Debugging log

    def send_magnet(self, magnet_link):
        url = f"{API_BASE}/transfer/create"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"src": magnet_link}
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                json_response = response.json()
                if json_response.get("status") == "success":
                    return True
                else:
                    print(f"Error in send_magnet response: {json_response}")  # Debugging log
            else:
                print(f"HTTP Error: {response.status_code} - {response.text}")  # Debugging log
        except requests.RequestException as e:
            print(f"Network error during send_magnet: {e}")  # Debugging log
        return False

def load_token():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("token")  # Directly return the token without validation
        except Exception as e:
            print(f"Error reading config file: {e}")  # Debugging log
    return prompt_token()

def prompt_token():
    while True:
        token, ok = QInputDialog.getText(None, "Premiumize Token", "Enter your Premiumize API token:")
        if not ok:
            QMessageBox.critical(None, "Error", "Premiumize token is required to use this app.")
            exit(1)
        # Save the token without validation
        with open(CONFIG_FILE, "w") as f:
            json.dump({"token": token}, f)
        return token

def validate_token(token):
    # Skip validation entirely
    return True

def load_or_prompt_token():
    return load_token()
