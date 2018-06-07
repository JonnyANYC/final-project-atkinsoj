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
        # TODO: Move to the model.
        device = Device(parent=user.key, name=request_data["name"], type=request_data["type"],
                        width=int(request_data["width"]), height=int(request_data["height"]),
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

        # FIXME: Fetch a random image from Unsplash and include in the response.
        # FIXME: Add orientation to the kind
        headers = dict()  # Authorization="Client-ID " + get_unsplash_app_settings()["access_key"])
        #headers = dict(Authorization="Bearer " + "3c06d01d86871c04433aa26874c356458123b7304d000c4bccb702033f3c7c2a")  # user.unsplash_token)
        headers["Accept-Version"] = "v1"
        payload = dict(per_page=1, query=device.image_query, client_id=get_unsplash_app_settings()["access_key"])
        photo_search_url = "https://api.unsplash.com/search/photos?" + urllib.urlencode(payload)
        response_code, response_json = fetch_json(photo_search_url, None, headers)

        if response_code != 200 or not response_json:
            send_error(self.response, 500, "Unsplash search request failed. e and url and headers: " + str(response_json) + " " + photo_search_url + " " + str(headers))
            return

        photo_id = response_json["results"][0]["id"]
        payload = dict(w=device.width, h=device.height, client_id=get_unsplash_app_settings()["access_key"])
        photo_request_url = "https://api.unsplash.com/photos/" + photo_id + "?" + urllib.urlencode(payload)
        response_code, response_json = fetch_json(photo_request_url, None, headers)

        if response_code != 200 or not response_json:
            send_error(self.response, 500, "Unsplash photo request failed")
            return

        photo_url = response_json["urls"]["custom"]
        # FIXME: use this class or get rid of it.
        UnsplashPhoto(device.width, device.height, device.image_query)

        device_json = device.to_json_ready()
        device_json["photo_url"] = photo_url

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
        if "type" in request_data and request_data["type"]:
            device.type = request_data["type"]
        if "height" in request_data and request_data["height"]:
            device.height = int(request_data["height"])
        if "width" in request_data and request_data["width"]:
            device.width = int(request_data["width"])
        if "image_query" in request_data and request_data["image_query"]:
            device.image_query = request_data["image_query"]

        device.put()

        send_success(self.response, json.dumps(device.to_json_ready()))

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

    def __init__(self, width, height, query):
        self.photo_url = None
        self.photo_title = None
        self.author_name = None
        self.author_profile_url = None
        self._query(width, height, query)

    def _query(self, width, height, query):
        self.photo_url = "https://unsplash.com/photos/D1wiHCovGJ0"
        self.photo_title = "Just Hanging Around"
        self.author_name = "Erda Estremera"
        self.author_profile_url = "https://unsplash.com/@erdaest"
