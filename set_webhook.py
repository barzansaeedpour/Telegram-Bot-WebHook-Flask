import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Ngrok URL (or your domain)
# DOMAIN = "https://584e-173-239-224-34.ngrok-free.app"
DOMAIN = "https://9a03-172-98-33-108.ngrok-free.app"

# Construct the webhook URL with token
WEBHOOK_URL = f"{DOMAIN}/webhook/{TOKEN}"

# Set the webhook
res = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
print(res.json())
