from google.appengine.ext import ndb


# The Model classes were adapted from my work on Assignment 3.
class User(ndb.Model):
    """
    My User model
    """

    # id = auto-gen by Google Cloud Datastore. Unsplash ID is unique, but I don't want to include that in a public key.
    unsplash_token = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    default_image_query = ndb.StringProperty(required=True)
    favorite_topics = ndb.StringProperty()

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
        user = cls.query().filter(User.unsplash_token == external_id).fetch(1)
        return user

    def to_public_json_ready(self):
        user_public_json_ready = dict(id=self.key.id(), name=self.name, self="/users/" + str(self.key.id()))
        return user_public_json_ready

    def to_json_ready(self):
        # Security is not handled by the model.
        user_json_ready = dict(id=self.key.id(), name=self.name, email=self.email,
                                 default_image_query=self.default_image_query, favorite_topics=self.favorite_topics,
                                 self="/users/" + str(self.key.id()))
        return user_json_ready
