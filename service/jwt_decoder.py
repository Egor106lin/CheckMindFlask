from jwt import decode

def jwt_decode(jwt_string: str, alg: list = ["RS256"]) -> dict:
    res = decode(jwt_string, algorithms=alg, options={"verify_signature": False})
    return res