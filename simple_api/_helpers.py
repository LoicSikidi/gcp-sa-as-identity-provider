import os

def get_issuer() -> str:
    return os.environ['SERVICE_ACCOUNT_ISSUER']

def get_jwk_url() -> str:
    return f'https://www.googleapis.com/robot/v1/metadata/jwk/{get_issuer()}'

def get_audience() -> str:
    return os.getenv('API_AUDIENCE', 'simple_api')

def is_bearer_token(header: str) -> bool:
    if len(arr := header.split(" ")) < 1:
        return False
    if arr[0] != "Bearer":
        return False
    return True

def extract_jwt_from_header(header: str) -> str:
    return header.split(" ")[1]