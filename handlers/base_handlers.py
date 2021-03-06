
from google.appengine.api import users
import webapp2
from webapp2_extras import sessions
import json

import main

from email import email

# Potentially helpful (or not) superclass for *logged in* pages and actions (assumes app.yaml gaurds for login)

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

### Pages ###
class BasePage(BaseHandler):
    """Page handlers should inherit from this one."""
    def get(self):
        user = users.get_current_user()
        if not user and "user_info" not in self.session:
            self.redirect("/")
            return
        email = ""
        values = {}
        if user:
            email = user.email().lower()
            values = {"user_email": email,
                      "logout_url": users.create_logout_url("/")}
        else:
            email = json.loads(self.session["user_info"])["email"]
            values = {"user_email": email,
                      "logout_url": "/logout"} 
        
        self.update_values(email, values)  
        template = main.jinja_env.get_template(self.get_template())
        self.response.out.write(template.render(values))


    def update_values(self, email, values):
        # Subclasses should override this method to add additional data for the Jinja template.
        pass


    def get_template(self):
        # Subclasses must override this method to set the Jinja template.
        raise Exception("Subclass must implement handle_post!")



### Actions ###

class BaseAction(BaseHandler):
    """ALL action handlers should inherit from this one."""
    def post(self):
        user = users.get_current_user()
        if not user and "user_info" not in self.session:
            raise Exception("Missing user!")
        email = ""
        if user:
            email = user.email().lower()
        else:
            email = json.loads(self.session["user_info"])["email"]
        self.handle_post(email)  # TODO: Update what is passed to subclass function as needed


    def get(self):
        self.post()  # Action handlers should not use get requests.


    def handle_post(self, email):
        # Subclasses must override this method to handle the request.
        raise Exception("Subclass must implement handle_post!")
