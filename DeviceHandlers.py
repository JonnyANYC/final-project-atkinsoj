import json
import urllib

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
            devices_json.append(device.to_json_ready())

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

        # parent assignment taken from the Google Cloud Datastore docs (ndb/creating-entity-keys).
        device = Device(parent=user.key, name=request_data["name"], width=int(request_data["width"]),
                        height=int(request_data["height"]), orientation=request_data["orientation"],
                        image_query=request_data["image_query"])
        device.put()

        send_success(self.response, json.dumps(device.to_json_ready()))

    def get_auth(self):
        return User.get_by_external_id(get_auth_token(self.request))


class DeviceHandler(webapp2.RequestHandler):

    def get(self, device_id):

        # FIXME: Error handling

        user = self.get_auth()

        if not user:
            send_error(self.response, 401)
            return

        device = Device.get_by_id(user.key.id(), device_id)

        if not device:
            send_error(self.response, 404)
            return

        photo = UnsplashPhoto()
        photo.query(device.width, device.height, device.orientation, device.image_query)

        if photo.response_code != 200:
            send_error(self.response, 500, photo.response_json)
            return

        device_json = device.to_json_ready()
        device_json["photo_url"] = photo.photo_url

        send_success(self.response, json.dumps(device_json))

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
        if "height" in request_data and request_data["height"]:
            device.height = int(request_data["height"])
        if "width" in request_data and request_data["width"]:
            device.width = int(request_data["width"])
        if "orientation" in request_data and request_data["orientation"]:
            device.orientation = int(request_data["orientation"])
        if "image_query" in request_data and request_data["image_query"]:
            device.image_query = request_data["image_query"]

        device.put()

        photo = UnsplashPhoto()
        photo.query(device.width, device.height, device.orientation, device.image_query)

        if photo.response_code != 200:
            send_error(self.response, 500, photo.response_json)
            return

        device_json = device.to_json_ready()
        device_json["photo_url"] = photo.photo_url

        send_success(self.response, json.dumps(device_json))

    def delete(self, device_id):

        # TODO: Error handling

        user = self.get_auth()

        if not user:
            send_error(self.response, 401)
            return

        device = Device.get_by_id(user.key.id(), device_id)

        if not device:
            send_error(self.response, 404)
            return

        device.key.delete()

        send_success(self.response, None)

    def get_auth(self):
        return User.get_by_external_id(get_auth_token(self.request))


class UnsplashPhoto:

    def __init__(self):
        self.photo_url = None
        self.photo_title = None
        self.author_name = None
        self.author_profile_url = None
        self.response_code = -1
        self.response_json = None

    def query(self, width, height, orientation, image_query):

        headers = dict()  # Authorization="Client-ID " + get_unsplash_app_settings()["access_key"])
        headers["Accept-Version"] = "v1"
        payload = dict(client_id=get_unsplash_app_settings()["access_key"], query=image_query,
                       orientation=orientation, per_page=1)
        photo_search_url = "https://api.unsplash.com/search/photos?" + urllib.urlencode(payload)
        response_code, response_json = fetch_json(photo_search_url, None, headers)

        if response_code != 200 or not response_json:
            self.response_code = 500
            self.response_json = '{"Error": "' + response_code + ': Unsplash search request failed.",'
            '"ErrorMessage": "' + response_json + '"}'
            return self

        photo_id = response_json["results"][0]["id"]
        payload = dict(client_id=get_unsplash_app_settings()["access_key"], w=width, h=height)
        photo_request_url = "https://api.unsplash.com/photos/" + photo_id + "?" + urllib.urlencode(payload)
        response_code, response_json = fetch_json(photo_request_url, None, headers)

        if response_code != 200 or not response_json:
            self.response_code = 500
            self.response_json = '{"Error": "' + response_code + ': Unsplash photo request failed.",'
            '"ErrorMessage": "' + response_json + '"}'
            return self

        self.photo_url = response_json["urls"]["custom"]
        self.photo_title = response_json["urls"]["custom"]
        self.author_name = response_json["user"]["name"]
        self.author_profile_url = response_json["user"]["links"]["html"]
        self.response_code = 200
        self.response_json = response_json

        return self
