# utils/api.py

import requests

BASE_URL = "http://127.0.0.1:8000"


class APIClient:

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
                "status": "ERROR",
                "message": str(e)
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
                "status": "ERROR",
                "message": str(e)
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
                "status": "ERROR",
                "message": str(e)
            }


api_client = APIClient()