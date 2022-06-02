from datetime import datetime
from typing import Optional
import logging

from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse

import _helpers
import models.users as users
from schemas.token import TokenResponse
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

jwt = Jwt(service_account_key_path=_helpers.get_service_account_key_path())
users.generate_fake_users()

@app.post("/token", response_model=TokenResponse)
def token(username: str = Form(), password: str = Form(), grant_type: str = Form(), scope: Optional[str] = Form(None)):
    if grant_type != "password":
        raise UnicornException(
            status_code=400,
            body={"error":"invalid_grant"}
        )        
    if (user := users.get_user(username=username, password=password)) is None:
        raise UnicornException(
            status_code=401,
            body={"error":"unauthorized"}
        )
    try:
        access_token = jwt.encode(additional_claims={"sub":user.id, "role": user.role})
    except Exception as err:
        logging.error(f'Error during signing phase. Root cause: {format(err)}')
        raise UnicornException(
            status_code=500,
            body={"error":"internal_error"}
        )
    expiration_timestamp = _helpers.get_exp_from_encoded_jwt(jwt=access_token)
    expires_in = _helpers.diff_in_seconds_between_now_and_timestamp(datetime.fromtimestamp(expiration_timestamp))
    return TokenResponse(access_token=access_token, expires_in=expires_in)
