import secrets


def get_cookies() -> dict[str, str]:
    cookies: dict[str, str] = {"_autolab3_session": secrets.AUTOLAB_SESSION_COOKIE}
    return cookies
