from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Header, HTTPException, Form, Request
from fastapi.responses import JSONResponse

import _helpers
from schemas.game import Game
from services.jwt import Jwt

app = FastAPI()

class UnicornException(Exception):
    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self.body = body

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.body,
    )

jwt = Jwt(jwks_endpoint=_helpers.get_jwk_url(), algorithms=["RS256"], issuer=_helpers.get_issuer(), audience=_helpers.get_audience())

@app.get("/api/v1/games", response_model=List[Game])
def get_games(authorization: str = Header(default=None)):
    if _helpers.is_bearer_token(authorization) is False:
        raise UnicornException(
            status_code=400,
            body={"error":"invalid_authorization_header"}
        )
    access_token = _helpers.extract_jwt_from_header(authorization) 
    try:
        claims = jwt.decode(jwt=access_token)
    except Exception as err:
        print(format(err))
        raise UnicornException(
            status_code=401,
            body={"error":"unauthorized"}
        ) 
 
    print(f'logged user id: {claims["sub"]}')
    print(f'logged user\'s role: {claims["role"]}')

    return [
        Game(name="Call of Duty: Modern Warfare II", platform="PS5", timespend=8000),
        Game(name="Grand Theft Auto V", platform="PS4", timespend=100),
    ]
