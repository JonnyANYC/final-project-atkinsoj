#!/usr/bin/env python

import webapp2
from DeviceHandlers import DeviceListHandler, DeviceHandler
from UserHandlers import UserListHandler, UserHandler

# A class for favorited images? tags/collection, like/love, my description, etc.


# Patch for "PATCH", taken from the "GAE Demo" video from the course.
# FIXME: Remove this and use PUT instead.
# allowed_methods = webapp2.WSGIApplication.allowed_methods
# new_allowed_methods = allowed_methods.union(('PATCH',))
# webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/users', UserListHandler),
    ('/users/(\d+)', UserHandler),
    ('/devices', DeviceListHandler),
    ('/devices/(\d+)', DeviceHandler),
], debug=True)
