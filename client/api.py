import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils import get_hwid
import socket

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# REPLACE "http://127.0.0.1:5001" with your actual server URL.
# Example: "http://123.45.67.89:5001" or "https://license.myapp.com"
SERVER_URL = "http://127.0.0.1:5001" 
# ---------------------------------------------------------

class LicenseClient:
    def __init__(self):
        self.session = requests.Session()
        self.hwid = get_hwid()
        self._setup_retries()

    def _setup_retries(self):
        """
        Configures the session to retry failed connections automatically.
        This handles temporary network blips.
        """
        retry_strategy = Retry(
            total=3,  # Retry 3 times
            backoff_factor=1,  # Wait 1s, then 2s, then 4s...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def validate_key(self, key):
        """
        Validates the key with the server.
        Returns (success, message, data).
        """
        payload = {
            "key": key,
            "hwid": self.hwid
        }
        
        try:
            # timeout=(connect_timeout, read_timeout)
            response = self.session.post(
                f"{SERVER_URL}/validate", 
                json=payload, 
                timeout=(5, 10),
                verify=True # Verify SSL certificates
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, "Valid", data
            elif response.status_code == 404:
                return False, "Invalid Key", None
            elif response.status_code == 403:
                msg = response.json().get("message", "Access Denied")
                return False, msg, None
            else:
                return False, f"Server Error ({response.status_code})", None

        except requests.exceptions.ConnectionError as e:
            # Differentiate connection refused vs internet issues
            return False, "Connection Failed.\nCheck Internet or Proxy.", None
        except requests.exceptions.Timeout:
            return False, "Connection Timed Out.\nServer might be slow.", None
        except requests.exceptions.SSLError:
            return False, "Security Error.\nTime/Date or Cert issue.", None
        except Exception as e:
            return False, f"Error: {str(e)}", None
