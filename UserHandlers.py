from urllib import urlencode
import webapp2
import Device
from User import User
from Utils import *


# The basic approach for my list handlers is taken from my work on Assignment 3.
class UserListHandler(webapp2.RequestHandler):

    def get(self):

        users = User.get_all()

        # TODO: Fetch the full details, for the current user only? Maybe not.
        # What if the auth creds are invalid? Should we reject this request? Maybe not.

        users_json = []
        for user in users:
            users_json.append(user.to_json_ready())

        send_success(self.response, json.dumps(users_json))

    def post(self):
        request_data = json.loads(self.request.body)

        # TODO: Not thread-safe!! But probably not an issue in this course.
        # TODO: Move to the model.
        existing = User.query().filter(User.unsplash_token == request_data["unsplash_token"]).fetch(1)
        if existing:
            send_error(self.response, 400,
                       response_message_json("FAILURE",
                                             "Users should be unique: {}".format(request_data["unsplash_token"])))
            return

        # Set empty values in the input if they need to be overridden by the data in Unsplash.
        if "name" not in request_data:
            request_data["name"] = None
        if "location" not in request_data:
            request_data["location"] = None
        if "url" not in request_data:
            request_data["url"] = None

        unsplash_user = UnsplashUser(request_data["unsplash_username"], request_data["name"],
                                     request_data["location"], request_data["url"])
        unsplash_user.lookup_unsplash_profile()

        user = User(unsplash_token=request_data["unsplash_token"], name=unsplash_user.name,
                    unsplash_username=request_data["unsplash_username"], location=unsplash_user.location,
                    url=unsplash_user.url, default_image_query=request_data["default_image_query"])
        user.put()

        send_success(self.response, json.dumps(user.to_private_json_ready()))


class UserHandler(webapp2.RequestHandler):

    def get(self, user_id):

        user = User.get_by_id(long(user_id))

        # FIXME: Error handling

        if not user:
            send_error(self.response, 404)
            return

        auth_user = self.get_auth()

        if auth_user and auth_user.key.id() == user.key.id():
            send_success(self.response, json.dumps(user.to_private_json_ready()))
        else:
            send_success(self.response, json.dumps(user.to_json_ready()))

    def put(self, user_id):

        user = User.get_by_id(user_id)

        # FIXME: Error handling

        if not user:
            send_error(self.response, 404)
            return

        auth_user = self.get_auth()
        if (not auth_user) or auth_user.key.id() != user.key.id():
            send_error(self.response, 401)
            return

        # FIXME: Fetch Unsplash profile and use those values where needed

        request_data = json.loads(self.request.body)
        if "name" in request_data and request_data["name"]:
            user.name = request_data["name"]
        if "location" in request_data and request_data["location"]:
            user.location = request_data["location"]
        if "url" in request_data and request_data["url"]:
            user.url = request_data["url"]
        if "default_image_query" in request_data and request_data["default_image_query"]:
            user.default_image_query = request_data["default_image_query"]

        user.put()

        send_success(self.response, json.dumps(user.to_private_json_ready()))

    def delete(self, user_id):

        user = User.get_by_id(user_id)

        if not user:
            send_error(self.response, 404)
            return

        auth_user = self.get_auth()
        if (not auth_user) or auth_user.key.id() != user.key.id():
            send_error(self.response, 401)
            return

        # FIXME: Error handling

        # Delete devices as well.
        devices = Device.get_by_user_id(user_id)
        for device in devices:
            device.key.delete()

        user.key.delete()

        send_success(self.response, None)

    def get_auth(self):
        return User.get_by_external_id(get_auth_token(self.request))


class UnsplashUser:

    def __init__(self, username, name=None, location=None, url=None):
        self.username = username
        self.name = name
        self.location = location
        self.url = url

    def lookup_unsplash_profile(self):

        headers = dict()  # Authorization="Client-ID " + get_unsplash_app_settings()["access_key"])
        headers["Accept-Version"] = "v1"
        payload = dict(client_id=get_unsplash_app_settings()["access_key"])
        user_profile_url = "https://api.unsplash.com/users/" + self.username + "?" + urlencode(payload)
        response_code, response_json = fetch_json(user_profile_url, None, headers)

        if response_code != 200 or not response_json:
            return

        if (not self.name) and response_json["name"]:
            self.name = response_json["name"]
        if (not self.location) and response_json["location"]:
            self.location = response_json["location"]
        if (not self.url) and response_json["portfolio_url"]:
            self.url = response_json["portfolio_url"]

        return self
