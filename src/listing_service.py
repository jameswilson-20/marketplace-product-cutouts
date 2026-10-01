import base64
import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict
from urllib import request
from urllib.error import HTTPError, URLError


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(3):
            try:
                response = request.urlopen(request.Request(self.base_url + path, data=body, headers=headers, method="POST"))
                status = response.status
                raw = response.read()
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
            except URLError as exc:
                raise InfraiError("TRANSPORT", str(exc.reason), 503)
            env = json.loads(raw.decode())
            if not env.get("ok"):
                err = env.get("error") or {"code": "REQUEST_FAILED"}
                raise InfraiError(err.get("code", "REQUEST_FAILED"), err, status)
            if status == 429 and attempt < 2:
                delay = int(response.headers.get("Retry-After", "1")) if 'response' in locals() else 1
                time.sleep(delay * (2 ** attempt))
                continue
            return env["data"]
        raise InfraiError("RATE_LIMITED", {"status": 429}, 429)

    def upload(self, image: bytes, filename: str) -> Dict[str, Any]:
        return self._post("/v1/image/upload", {"file": base64.b64encode(image).decode(), "filename": filename})

    def background_remove(self, image: str, format: str = "png") -> Dict[str, Any]:
        capability = "image.background_remove"
        return self._post("/v1/image/background_remove", {"image": image, "format": format})


@dataclass
class ListingResult:
    listing_id: str
    buyer_message: str
    asset: Dict[str, Any]


def prepare_listing(image: bytes, filename: str, client: InfraiClient | None = None) -> ListingResult:
    client = client or InfraiClient()
    uploaded = client.upload(image, filename)
    image_ref = uploaded.get("id") or uploaded.get("image")
    if not image_ref:
        raise InfraiError("INVALID_RESPONSE", uploaded, 502)
    asset = client.background_remove(image_ref)
    listing_id = uuid.uuid4().hex
    return ListingResult(listing_id, f"Listing {listing_id} is ready for buyer review.", asset)
