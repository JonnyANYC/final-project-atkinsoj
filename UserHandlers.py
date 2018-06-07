import json
import webapp2
import Device
from User import User
from Utils import *
import logging


# The basic approach for my list handlers is taken from my work on Assignment 3.
class UserListHandler(webapp2.RequestHandler):

    def get(self):

        users = User.get_all()

        # TODO: Fetch the full details for the current user (if authenticated)?
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

        # TODO: Fetch the user details from Unsplash, and use the Unsplash profile details as defaults.

        user = User(unsplash_token=request_data["unsplash_token"], name=request_data["name"],
                    email=request_data["email"], default_image_query=request_data["default_image_query"],
                    favorite_topics=request_data["favorite_topics"])
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

        request_data = json.loads(self.request.body)
        if "name" in request_data and request_data["name"]:
            user.name = request_data["name"]
        if "email" in request_data and request_data["email"]:
            user.email = request_data["email"]
        if "default_image_query" in request_data and request_data["default_image_query"]:
            user.default_image_query = request_data["default_image_query"]
        if "favorite_topics" in request_data and request_data["favorite_topics"]:
            user.favorite_topics = request_data["favorite_topics"]

        user.put()

        send_success(self.response, json.dumps(user.to_private_json_ready()))

    def delete(self, user_id):

        send_error(self.response, 500)
        test = 5
        if 5 == test:
            return

        user = User.get_by_id(user_id)

        # FIXME: Check creds!
        # FIXME: Error handling

        # FIXME: Delete devices as well.
        devices = Device.find_devices_by_user_id(user_id)

        user.delete()

        send_success(self.response, None)

    def get_auth(self):
        return User.get_by_external_id(get_auth_token(self.request))
