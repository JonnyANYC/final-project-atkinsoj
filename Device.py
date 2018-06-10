from google.appengine.ext import ndb
from User import User
import logging


class Device(ndb.Model):
    # id = auto-gen by Google Cloud Datastore, because device name can change.
    # parent = User
    name = ndb.StringProperty(required=True)
    width = ndb.IntegerProperty(required=True)
    height = ndb.IntegerProperty(required=True)
    orientation = ndb.StringProperty(required=True)
    image_query = ndb.StringProperty(required=True)

    @classmethod
    def get_by_user_id(cls, user_id):
        # TODO: Accept a key instead. I think in most/all cases I already have the user key.
        # TODO: Pagination. Currently this function only handles up to 30 devices per user.
        user_key = ndb.Key(User, long(user_id))
        # Ancestor query logic taken from the Google Cloud Datastore documentation.
        devices = cls.query(ancestor=user_key).fetch(30)
        return devices

    @classmethod
    def get_by_user_and_urlsafe_id(cls, user_id, device_id_urlsafe):
        # In a full-fledged app, I would also have a simpler get_by_urlsafe_id() method that didn't require a user ID.
        # For now, I'm using just this one method to fetch a device, and including the user-checking logic here.
        # "urlsafe" key logic taken from the Google Cloud Datastore / ndb documentation.
        device_key = ndb.Key(urlsafe=device_id_urlsafe)

        if device_key.parent().id() != long(user_id):
            # Parent mis-match. Unauthorized or invalid request.
            return None

        device = device_key.get()
        return device

    def to_json_ready(self):
        device_json_ready = dict(id=self.key.urlsafe(), name=self.name, width=self.width, height=self.height,
                                 orientation=self.orientation, image_query=self.image_query,
                                 owner="/users/" + str(self.key.id()), self="/devices/" + str(self.key.urlsafe()),
                                 devices="/devices")
        return device_json_ready
