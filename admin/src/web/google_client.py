from os import environ
from oauthlib.oauth2 import WebApplicationClient


client = WebApplicationClient(environ.get("GOOGLE_CLIENT_ID"))
