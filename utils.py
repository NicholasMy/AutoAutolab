from typing import Dict

import secrets


def get_cookies() -> Dict[str, str]:
    cookies: Dict[str, str] = {
        "_autolab3_session": secrets.AUTOLAB_SESSION_COOKIE
    }
    return cookies
