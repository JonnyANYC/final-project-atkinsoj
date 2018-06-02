from google.appengine.ext import ndb


# The Model classes were adapted from my work on Assignment 3.
class User(ndb.Model):
    """
    My User model
    """

    # id = auto-gen by Google Cloud Datastore. External ID is unique, but I don't want to include that in a public key.
    external_id = ndb.IntegerProperty(required=True)
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    default_image_query = ndb.StringProperty(required=True)
    summary_bio = ndb.StringProperty(required=True)

    @classmethod
    def get_by_id(cls, user_id):
        user = ndb.Key(User, long(user_id)).get()
        return user

    @classmethod
    def get_all(cls):
        users = cls.query().fetch(30)
        return users

    @classmethod
    def get_by_external_id(cls, external_id):
        user = cls.query().filter(User.external_id == external_id).fetch(1)
        return user

    def to_public_json_ready(self):
        user_public_json_ready = dict(id=self.key.id(), name=self.name, summary_bio=self.summary_bio,
                                      self="/users/" + str(self.key.id()))
        return user_public_json_ready

    def to_json_ready(self):
        # Security is not handled by the model.
        device_json_ready = dict(id=self.key.id(), name=self.name, email=self.email,
                                 default_image_query=self.default_image_query, summary_bio=self.summary_bio,
                                 self="/users/" + str(self.key.id()))
        return device_json_ready
