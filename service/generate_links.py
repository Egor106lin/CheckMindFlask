from service.config import config
from urllib import parse

def generate_google_url(state: str = None) -> str:
    '''This function generate url to redirect user here after button "google"'''
    query_params = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile email",
        "access_type": "offline",
        "prompt": "consent"
    }
    if state:
        query_params["state"] = state
    query_string = parse.urlencode(query_params, quote_via=parse.quote)
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return f"{base_url}?{query_string}"


def generate_vk_url(code_challenge: str, state: str = None) -> str:
    '''This function generate url to redirect user here after button "vk"'''
    query_params = {
        "client_id": config.VK_CLIENT_ID,
        "redirect_uri": config.VK_REDIRECT_URI,
        "response_type": "code",
        "scope": "vkid.personal_info email",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    if state:
        query_params["state"] = state
    query_string = parse.urlencode(query_params, quote_via=parse.quote)
    base_url = "https://id.vk.ru/authorize"
    return f"{base_url}?{query_string}"