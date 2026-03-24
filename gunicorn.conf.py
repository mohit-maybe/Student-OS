import os

# Render sets the PORT environment variable to 10000 by default
port = os.getenv("PORT", "10000")
bind = f"0.0.0.0:{port}"
workers = 1
