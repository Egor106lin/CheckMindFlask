from jwt import decode, encode
from service.config import settings


def jwt_decode(jwt_string: str, alg: list = ["RS256"]) -> dict:
    res = decode(jwt_string, algorithms=alg, options={"verify_signature": False})
    return res


def jwt_encode(data) -> str:
    return encode(
        data,
        settings.JOIN_SECRET,
        algorithm='HS256'
    )