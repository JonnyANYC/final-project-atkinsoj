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

