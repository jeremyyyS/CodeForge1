# utils/api.py

import os
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


class APIClient:

    def health_check(self):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def optimize(self, code: str):
        try:
            response = requests.post(
                f"{BASE_URL}/optimize",
                json={"code": code},
                timeout=120
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Backend unavailable: {str(e)}"
            }

    def optimize_rules_only(self, code: str):
        try:
            response = requests.post(
                f"{BASE_URL}/optimize-rules-only",
                json={"code": code},
                timeout=120
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Backend unavailable: {str(e)}"
            }

    def upload_file(self, file_bytes, filename: str):
        try:
            files = {
                "file": (filename, file_bytes, "text/x-python")
            }

            response = requests.post(
                f"{BASE_URL}/upload",
                files=files,
                timeout=120
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Backend unavailable: {str(e)}"
            }


api_client = APIClient()
