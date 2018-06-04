from unsplash_app_settings import unsplash_app_settings


def get_auth_token(request):
    if "Authorization" not in request.headers:
        return None

    auth_token = request.headers["Authorization"]

    if not auth_token.startswith("Bearer "):
        return None

    return auth_token[7:]


# Taken from my work on Assignment 3.
def send_success(response, body):
    if body:
        response.status = 200
        response.charset = "utf-8"
        response.content_type = 'application/json'  # ; charset=utf-8'
        response.write(body)
    else:
        response.status = 204


# Taken from my work on Assignment 3.
def send_error(response, code, body=None):
    response.status = code
    if body:
        response.charset = "utf-8"
        response.content_type = 'application/json'  # ; charset=utf-8'
        response.write(body)


# Taken from my work on Assignment 3.
def response_message_json(status, message):
    return '{"status": "' + status + '", "message": "' + message + '"}'


def get_unsplash_app_settings():
    return unsplash_app_settings()
