import json
import webapp2
from Device import Device
import User
from Utils import *


# The basic approach for my list handlers is taken from my work on Assignment 3.
# TODO: Move the device model and handlers to a separate file.
class DeviceListHandler(webapp2.RequestHandler):

    def get(self):
        user = User.get_by_external_id(self.get_auth())

        # FIXME: Handle missing user

        devices = Device.get_by_user_id(user.key.id())

        devices_json = []
        for device in devices:
            devices_json.append(device.to_json_ready())

        send_success(self.response, json.dumps(devices_json))

    def post(self):
        request_data = json.loads(self.request.body)

        # TODO: Not thread-safe!! But probably not an issue in this course.
        user = User.get_by_external_id(self.get_auth())
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
        return self.request.query["token"]


# The basic approach for my entity handlers is taken from my work on Assignment 3.
class DeviceHandler(webapp2.RequestHandler):

    def get(self, device_id):

        # FIXME: Error handling

        user = User.get_by_external_id(self.get_auth())

        # FIXME: Handle auth error (everywhere)

        device = Device.get_by_id(user.key.id(), device_id)

        # FIXME: Fetch a random image from Unsplash and include in the response.

        if not device:
            send_error(self.response, 404)
            return

        send_success(self.response, json.dumps(device.to_json_ready()))

    def put(self, device_id):

        # FIXME: Error handling

        user = User.get_by_external_id(self.get_auth())

        # FIXME: Handle auth error (everywhere)

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

        send_success(self.response, json.dumps(device.to_json_ready()))

    def delete(self, device_id):

        send_error(self.response, 500)
        test = 5
        if 5 == test:
            return

        # FIXME: Error handling

        user = User.get_by_external_id(self.get_auth())

        # FIXME: Handle auth error (everywhere)

        device = Device.get_by_id(user.key.id(), device_id)

        if not device:
            send_error(self.response, 404)
            return

        device.delete()

        send_success(self.response, None)

    def get_auth(self):
        return self.request.query["token"]

