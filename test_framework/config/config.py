"""Environment settings for the test run.

Every value can be overridden with an environment variable, or on the command
line with `robot --variable NAME:value`.
"""
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
BROWSER = os.getenv("BROWSER", "chrome")
# Selenium server to drive the browser through, e.g. http://localhost:4444. Unset runs a local browser.
REMOTE_URL = os.getenv("REMOTE_URL") or None
TIMEOUT = os.getenv("TIMEOUT", "5s")
WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1366"))
WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "900"))

ADMIN = {
    "username": os.getenv("ADMIN_USER", "admin"),
    "password": os.getenv("ADMIN_PASSWORD", "admin123"),
}
SHOPPER = {
    "username": os.getenv("SHOPPER_USER", "user"),
    "password": os.getenv("SHOPPER_PASSWORD", "user123"),
}
