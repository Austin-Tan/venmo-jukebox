# *****************
# | Gmail section |
# *****************
EMAIL = "" # email address that receives your venmo notifs


# you need to be properly filtering the incoming payments as requests, which
# is easy to set up. consult the README under "Setup"
# uncomment and run get_label_ids() to fill these in:
REQUESTS_LABEL = ""
COMPLETED_LABEL = ""


# *******************
# | Spotify section |
# *******************

# grab this from your account settings on the Spotify browser client
USERNAME = ""

# after enabling development API connections to your account, you'll
# be given these
CLIENT_ID = ""
CLIENT_SECRET = ""

# this you can leave as the URI, just make sure to also set this on the
# Spotify app project you create on the Spotify developer site
REDIRECT_URI = "http://localhost:8888/callback"

# this is not entirely necessary, since a lot of times you can just tell
# the API to act on whatever device is currently playing. you can get this
# by uncommenting and running get_device_id()
DEVICE_ID = ""
