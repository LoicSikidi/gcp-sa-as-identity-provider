from typing import List

import jwt as jwt_client
from jwt import PyJWKClient

class Jwt():
    def __init__(self, jwks_endpoint:str, algorithms:List[str], issuer:str=None, audience:str=None):
        self.jwks_client = PyJWKClient(jwks_endpoint)
        self.algorithms = algorithms
        self.issuer = issuer
        self.audience = audience

    def decode(self, jwt:str) -> dict:
        signing_key = self.jwks_client.get_signing_key_from_jwt(jwt)
        return jwt_client.decode(
            jwt,
            signing_key.key,
            algorithms=self.algorithms,
            issuer=self.issuer,
            audience=self.audience
        )
