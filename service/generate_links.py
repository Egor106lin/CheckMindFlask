from service.config import settings
from urllib import parse

def generate_google_url(state: str = None) -> str:
    '''This function generate url to redirect user here after button "google"'''
    query_params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": "https://checkmind.nsforth.online/api/auth/google",
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