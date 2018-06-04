from google.appengine.ext import ndb
from User import User


class Device(ndb.Model):
    # id = auto-gen by Google Cloud Datastore, because device name can change.
    # parent = User
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    width = ndb.IntegerProperty(required=True)
    height = ndb.IntegerProperty(required=True)
    image_query = ndb.StringProperty(required=True)

    @classmethod
    def get_by_user_id(cls, user_id):
        # FIXME: Accept a key instead. I think in most/all cases I already have the user key.
        user_key = ndb.Key(User, long(user_id))
        devices = cls.query(ancestor=user_key).fetch(30)
        return devices

    @classmethod
    def get_by_id(cls, user_id, device_id):
        # Hierarchical key logic taken from the Google Cloud Datastore documentation.
        device = ndb.Key(User, long(user_id), cls, long(device_id)).get()
        return device

    def to_json_ready(self):
        device_json_ready = dict(id=self.key.id(), name=self.name, type=self.type, width=self.width, height=self.height,
                                 image_query=self.image_query, owner="/users/" + str(self.key.parent().id()),
                                 self="/devices/" + str(self.key.id()))
        return device_json_ready
