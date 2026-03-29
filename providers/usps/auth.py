from __future__ import annotations
import datetime as dt
import requests
from utils.exceptions import ProviderError

class USPSAuth:
    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: str | None = None
        self._expires_at: dt.datetime | None = None

    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def token(self) -> str:
        if not self.configured():
            raise ProviderError("USPS credentials are not configured.")
        if self._token and self._expires_at and dt.datetime.utcnow() < self._expires_at:
            return self._token
        resp = requests.post(f"{self.base_url}/oauth2/v3/token",
            json={"client_id": self.client_id, "client_secret": self.client_secret, "grant_type": "client_credentials"},
            timeout=30)
        if resp.status_code >= 400:
            raise ProviderError(f"USPS OAuth failed: {resp.status_code} {resp.text}")
        payload = resp.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise ProviderError(f"USPS OAuth response missing access_token: {payload}")
        expires_in = int(payload.get("expires_in", 3600))
        self._token = access_token
        self._expires_at = dt.datetime.utcnow() + dt.timedelta(seconds=max(60, expires_in - 60))
        return self._token
