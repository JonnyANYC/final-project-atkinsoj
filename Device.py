from google.appengine.ext import ndb
from User import User


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
        user_key = ndb.Key(User, long(user_id))
        # Ancestor query logic taken from the Google Cloud Datastore documentation.
        devices = cls.query(ancestor=user_key).fetch(30)
        return devices

    @classmethod
    def get_by_id(cls, user_id, device_id):
        # FIXME: Is this method redundant???
        # Hierarchical key logic taken from the Google Cloud Datastore documentation.
        device = ndb.Key(User, long(user_id), cls, long(device_id)).get()
        return device

    def to_json_ready(self):
        device_json_ready = dict(id=self.key.id(), name=self.name, width=self.width, height=self.height,
                                 orientation=self.orientation, image_query=self.image_query,
                                 owner="/users/" + str(self.key.parent().id()), self="/devices/" + str(self.key.id()))
        return device_json_ready
