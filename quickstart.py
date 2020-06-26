from __future__ import print_function
import pickle
import os.path
import base64

import spotipy
import authentication
from spotipy.oauth2 import SpotifyOAuth

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# target email address. 'me' also works for userId fields
USERID = authentication.EMAIL

# retrieved ID for the label "Requests"
# ## running original_request provides the IDs
LABELID = authentication.REQUESTS_LABEL

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    spotify_test()
    # messages_service(service)
    # original_request(service)


# test method for spotipy library
def spotify_test():
    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, username=authentication.USERNAME, client_id=authentication.CLIENT_ID, client_secret=authentication.CLIENT_SECRET, redirect_uri = authentication.REDIRECT_URI))

    results = sp.current_user_saved_tracks()
    # for idx, item in enumerate(results['items']):
    #     track = item['track']
    #     print(idx, track['artists'][0]['name'], " – ", track['name'])


# near-top level helper method to look through emails that have been labeled
# "Requests". i've set up a filter on gmail to categorize payments already
# calls get_message to retrieve contents once located
def messages_service(service):
    msg_resource = service.users().messages()
    res = msg_resource.list(userId='me', labelIds = LABELID).execute()
    if res == None:
        print("ERROR IN EXECUTING LIST REQUEST")
        return
    messages = res['messages']
    for message in messages:
        # print("Message Ids: " + str(message))
        get_message(msg_resource, message['id'])

# from a message/email id, return the contents. 
# this extracts the html, needs get_note to extract the payment comment/note
def get_message(resource, message_id):
    message = resource.get(userId='me', id=message_id).execute()
    if message == None:
        print("Message id " + str(message_id) + "invalid!!")
        return

    body = message.get("payload").get("body")
    coins = get_coins(message.get("payload").get("headers"))
    # print(coins)
    note = get_note(base64.urlsafe_b64decode(body.get("data")))
    # print(note)
    make_requests(coins, note)

# method queues a number of requests from the note given the coins inserted
# coins is a tuple(# of nickels inserted, # of cents over-paid)
# note is the note from the venmo transaction where we extract songs
def make_requests(coins, note):
    permitted = coins[0]
    refund = coins[1]
    requests = note
    print("Handling transaction with " + str(permitted) + " permitted requests, " + str(refund) + " too many cents, and songs:\n" + requests)

    delimiters = ("<br />", ",")
    # loop for if we have multiple requests. try to find a delimiter
    while permitted > 1:
        for delimiter in delimiters:
            start = requests.index(delimiter)
            if start != -1:
                song = requests[0:start]
                # print("Song is :" + str(song))
                permitted -= 1 if queue_song(song) else 0
                requests = requests[start + len(delimiter):]
                print("New requests: " + str(requests))
                break

    # queue the last request without looking to delimit
    if permitted == 1:
        permitted -= 1 if queue_song(requests) else 0

    print("Should refund " + str((permitted * 5) + refund) + " cents.")


# pass a song to search
# if found and queued successfully, return true, else false
def queue_song(song):
    print("Queueing " + str(song))
    return True


# returns a tuple with the number of nickels paid (divides payment by $0.05)
# and the number of cents remaining if any (not a multiple of 0.05)
def get_coins(headers):
    from decimal import Decimal
    subject = [i['value'] for i in headers if i["name"]=="Subject"][0]
    substring = subject[subject.index("$") + 1:]
    cents = int(Decimal(substring[:substring.index(".") + 3]) * Decimal(100))
    remainder = cents % 5
    # print("Cents is " + str(cents))
    return (int(cents / 5), remainder)

# goes through the passed html of the email and locates the note where
# user has left a comment on payment (the request), and returns just the note
def get_note(html):
    html = str(html)
    opening = html.index("<!-- note -->")
    html = html[opening:]
    opening = html.index("<p>")
    html = html[opening + 3:]
    closing = html.index("</p>")
    return(html[0: closing])



def original_request(service):
    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'] + ", id: " + label['id'])


if __name__ == '__main__':
    main()