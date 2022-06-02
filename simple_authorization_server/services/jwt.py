import json
import datetime
import logging

from google.cloud.iam_credentials_v1 import IAMCredentialsClient
from google.auth import _service_account_info

import _helpers

_DEFAULT_AUDIENCE = "simple_api"
_DEFAULT_TOKEN_LIFETIME_SECS = 3600  # 1 hour in seconds

class Jwt():
    def __init__(self, service_account_key_path: str = None):
        self.signing_method = "api" if service_account_key_path is None else "local"
        if self.signing_method == "local":
            info, signer = _service_account_info.from_filename(
                service_account_key_path, require=["client_email", "private_key_id"]
            )
            self.service_account_email = info["client_email"]
            self.service_account_key = info
            self.signer = signer
        else:
            self.service_account_email =  _helpers.get_sa_email()

    def _get_payload(self, additional_claims):
        now = _helpers.utcnow()
        lifetime = datetime.timedelta(seconds=_DEFAULT_TOKEN_LIFETIME_SECS)
        expiry = now + lifetime

        payload = {
            "iat": _helpers.datetime_to_secs(now),
            "exp": _helpers.datetime_to_secs(expiry),
            "iss": self.service_account_email,
            "aud": _DEFAULT_AUDIENCE
        }

        payload.update(additional_claims)

        return payload

    def _encode_with_service_account_key(self, payload: dict) -> str:
        key_id = self.service_account_key["private_key_id"]

        header = {
            "typ": "JWT",
            "alg": "RS256",
            "kid": key_id
        }

        segments = [
            _helpers.unpadded_urlsafe_b64encode(json.dumps(header).encode("utf-8")),
            _helpers.unpadded_urlsafe_b64encode(json.dumps(payload).encode("utf-8")),
        ]

        signing_input = b".".join(segments)
        signature = self.signer.sign(signing_input)
        segments.append(_helpers.unpadded_urlsafe_b64encode(signature))

        return b".".join(segments).decode("utf-8")

    def encode(self, additional_claims : dict) -> str:
        jwt = None
        if self.signing_method == "api":
            client = IAMCredentialsClient()
            endpoint = f'projects/-/serviceAccounts/{self.service_account_email}'
            jwt = client.sign_jwt(name=endpoint, payload=json.dumps(self._get_payload(additional_claims))).signed_jwt
        else:
            jwt = self._encode_with_service_account_key(self._get_payload(additional_claims))
        return jwt