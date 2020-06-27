from __future__ import print_function
import pickle
import os.path
import base64
import json
import time

import spotipy
import authentication
from spotipy.oauth2 import SpotifyOAuth

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.labels', 'https://www.googleapis.com/auth/gmail.modify']

# target email address. 'me' also works for userId fields
USERID = authentication.EMAIL

# retrieved ID for the label "Requests"
# ## running original_request provides the IDs
LABELID = authentication.REQUESTS_LABEL

# max length of songs to queue in ms. (isn't she lovely is 394000)
MAXLENGTH = 395000

SPOTIFY_SERVICE = None

def main():
    global SPOTIFY_SERVICE
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

    # service is top-level resource for gmail api after authorizing
    service = build('gmail', 'v1', credentials=creds)

    # spotify authentication
    scope = "streaming user-modify-playback-state user-read-playback-state user-read-private" # scope of authority
    # sp is top-level resource for spotify api after authorizing
    SPOTIFY_SERVICE = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, username=authentication.USERNAME, client_id=authentication.CLIENT_ID, client_secret=authentication.CLIENT_SECRET, redirect_uri = authentication.REDIRECT_URI))

    # spotify_test(SPOTIFY_SERVICE)
    # original_request(service)

    while True:
        messages_service(service)
        print("No new requests found, sleeping for another 5 seconds...")
        time.sleep(5)


# formats and prints a song name and artist
def format_song(song):
    title = song['name']
    artist = song['artists'][0]['name']
    millis = song['duration_ms']
    millis = int(millis)
    seconds = (millis/1000) % 60
    seconds = int(seconds)
    minutes = (millis/(1000*60)) % 60
    minutes = int(minutes)
    return "" + str(title) + " by " + str(artist) + " - " + str(minutes) + ":" + str(seconds)


# test method for spotipy library
# def spotify_test(service):
    # pretty_print(service.current_playback())
    # device_id = service.current_playback()['device']['id']
    # print("Id is " + str(device_id))
    # pretty_print(service.devices())
    # queue_song("in my life")
    # queue_song(service, "podcast")
    # if not is_playing(service):
    service.next_track()

# tries to search for passed song.
# if found, queue and return true.
# if not found, return false.
def queue_song(song):
    import re
    global SPOTIFY_SERVICE
    service = SPOTIFY_SERVICE

    if re.sub(r'\W+', '', song) == "skip":
        service.next_track(device_id=authentication.DEVICE_ID)
        print("Skipping current track...")
        return True

    res = service.search(q=song, type='track', market='US')
    count = res['tracks']['total']

    total = min(count, 10)
    i = 0
    while i < total:
        cur = res['tracks']['items'][i]
        # pretty_print(cur)
        if cur['duration_ms'] <= MAXLENGTH and cur['is_playable']:
            service.add_to_queue(cur['uri'], authentication.DEVICE_ID)
            if not is_playing(service):
                service.next_track()

            print("Queueing " + format_song(cur))
            return True

    # no songs found
    print("Could not find " + str(song))
    return False

# return true if currently playing a song, else false
def is_playing(service):
    if service.current_playback() == None:
        return False
    return service.current_playback()['is_playing']

# near-top level helper method to look through emails that have been labeled
# "Requests". i've set up a filter on gmail to categorize payments already
# calls process_message to retrieve contents once located
def messages_service(service):
    msg_resource = service.users().messages()
    res = msg_resource.list(userId='me', labelIds = LABELID).execute()
    if res == None:
        print("ERROR IN EXECUTING LIST REQUEST")
        return
    # pretty_print(res)
    if res['resultSizeEstimate'] == 0: # no matching emails
        return
    messages = res['messages']
    for message in messages:
        # print("Message Ids: " + str(message))
        process_message(msg_resource, message['id'])

# from a message/email id, return the contents. 
# this extracts the html, needs get_note to extract the payment comment/note
def process_message(resource, message_id):
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
    unlabel_message(resource, message_id)

# removes the "Requests" label from the message since we've processed it already
def unlabel_message(resource, message_id):
    new_body = {"addLabelIds":[authentication.COMPLETED_LABEL,], "removeLabelIds":[authentication.REQUESTS_LABEL,]}
    resource.modify(userId='me', id=message_id, body=new_body).execute()

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
        print("Top while loop, permitted: " + str(permitted) + " and requests: " + str(requests))
        split = False
        for delimiter in delimiters:
            start = requests.find(delimiter)
            if start != -1:
                song = requests[0:start]
                # print("Song is :" + str(song))
                permitted -= 1 if queue_song(song) else 0
                requests = requests[start + len(delimiter):]
                split = True
                break
            else:
                print("Couldn't find delimiter " + delimiter + " in str " + str(requests))

        if split == False:
            # only here if no delimiters found
            permitted -= 1 if queue_song(requests) else 0
            print("Should refund " + str((permitted * 5) + refund) + " cents.")
            return

    # queue the last request without looking to delimit
    if permitted == 1:
        if queue_song(requests):
            permitted -= 1
        else:
            for delimiter in delimiters:
                start = requests.find(delimiter)
                if start != -1:
                    song = requests[0:start]
                    # print("Song is :" + str(song))
                    permitted -= 1 if queue_song(song) else 0
                    requests = requests[start + len(delimiter):]
                    split = True
                    break
                else:
                    print("Couldn't find delimiter " + delimiter + " in str " + str(requests))
    print("Should refund " + str((permitted * 5) + refund) + " cents.")

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

# pretty prints passed json object
def pretty_print(target):
    print(json.dumps(target, indent=2))

# this was the sample code provided. not used
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