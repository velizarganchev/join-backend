def set_jwt_cookies(response, access_token, refresh_token, debug=False):
    cookie_params = {
        "httponly": True,
        "secure": not debug,
        "samesite": "Lax",
        "path": "/",
    }

    response.set_cookie("access_token", access_token, **cookie_params)
    response.set_cookie("refresh_token", refresh_token, **cookie_params)

    return response


def clear_jwt_cookies(response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return response
