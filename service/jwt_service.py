from jwt import decode, encode
from service.config import config


def jwt_decode(jwt_string: str, alg: list = ["RS256"]) -> dict:
    res = decode(jwt_string, algorithms=alg, options={"verify_signature": False})
    return res


def jwt_encode(data) -> str:
    return encode(
        data,
        config.JOIN_SECRET,
        algorithm='HS256'
    )