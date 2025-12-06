def set_jwt_cookies(response, access_token, refresh_token, debug=False):
    """
    Set correct JWT cookies for both DEV (localhost) and PROD (real domain).
    """

    if debug:
        # Localhost requires SameSite=None or cookies are blocked
        samesite = "None"
    else:
        # Production with same-site subdomains can use Lax
        samesite = "Lax"

    cookie_params = {
        "httponly": True,
        "secure": True,
        "samesite": samesite,
        "path": "/",
    }

    response.set_cookie("access_token", access_token, **cookie_params)
    response.set_cookie("refresh_token", refresh_token, **cookie_params)

    return response


def clear_jwt_cookies(response, debug=False):
    """
    Correctly delete cookies using same Site/Secure rules.
    """

    if debug:
        samesite = "None"
    else:
        samesite = "Lax"

    response.delete_cookie(
        "access_token", path="/", samesite=samesite)
    response.delete_cookie(
        "refresh_token", path="/", samesite=samesite)

    return response
