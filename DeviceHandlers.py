import json
import webapp2
from Device import Device
from User import User
from Utils import *


# The basic approach for my list handlers is taken from my work on Assignment 3.
# TODO: Move the device model and handlers to a separate file.
class DeviceListHandler(webapp2.RequestHandler):

    def get(self):
        user = self.get_auth()

        if not user:
            send_error(self.response, 401)
            return

        devices = Device.get_by_user_id(user.key.id())

        devices_json = []
        for device in devices:
            devices_json.append(device.to_private_json_ready())

        send_success(self.response, json.dumps(devices_json))

    def post(self):
        user = self.get_auth()

        if not user:
            send_error(self.response, 401)
            return

        request_data = json.loads(self.request.body)

        # TODO: Not thread-safe!! But probably not an issue in this course.
        # FIXME: Handle missing use
        existing = Device.query(ancestor=user.key).filter(Device.name == request_data["name"]).fetch(1)
        if existing:
            send_error(self.response, 400,
                       response_message_json("FAILURE",
                                             "Device name should be unique: {}".format(request_data["name"])))
            return

        device = Device(name=request_data["name"], type=request_data["type"],
                        width=request_data["width"], height=request_data["height"],
                        image_query=request_data["image_query"], parent=user.key)
        device.put()

        send_success(self.response, json.dumps(device.to_json_ready()))

    def get_auth(self):
        return User.get_by_external_id(get_auth_token(self.request))


# The basic approach for my entity handlers is taken from my work on Assignment 3.
class DeviceHandler(webapp2.RequestHandler):

    def get(self, device_id):

        # FIXME: Error handling

        user = self.get_auth()

        if not user:
            send_error(self.response, 401)
            return

        # FIXME: Handle auth error (everywhere)

        device = Device.get_by_id(user.key.id(), device_id)

        # FIXME: Fetch a random image from Unsplash and include in the response.

        if not device:
            send_error(self.response, 404)
            return

        send_success(self.response, json.dumps(device.to_private_json_ready()))

    def put(self, device_id):

        # FIXME: Error handling

        user = self.get_auth()

        if not user:
            send_error(self.response, 401)
            return

        device = Device.get_by_id(user.key.id(), device_id)

        request_data = json.loads(self.request.body)
        if "name" in request_data and request_data["name"]:
            device.name = request_data["name"]
        if "type" in request_data and request_data["type"]:
            device.type = request_data["type"]
        if "height" in request_data and request_data["height"]:
            device.height = request_data["height"]
        if "width" in request_data and request_data["width"]:
            device.width = request_data["width"]

        device.put()

        send_success(self.response, json.dumps(device.to_private_json_ready()))

    def delete(self, device_id):

        send_error(self.response, 500)
        test = 5
        if 5 == test:
            return

        # FIXME: Error handling

        user = self.get_auth()

        if not user:
            send_error(self.response, 401)
            return

        device = Device.get_by_id(user.key.id(), device_id)

        if not device:
            send_error(self.response, 404)
            return

        device.delete()

        send_success(self.response, None)

    def get_auth(self):
        return User.get_by_external_id(get_auth_token(self.request))


class UnsplashPhoto:

    def __init__(self, query):
        self.photo_url = None
        self.photo_title = None
        self.author_name = None
        self.author_profile_url = None

    def _query(self, query):
        self.photo_url = "https://unsplash.com/photos/D1wiHCovGJ0"
        self.photo_title = "Just Hanging Around"
        self.author_name = "Erda Estremera"
        self.author_profile_url = "https://unsplash.com/@erdaest"
