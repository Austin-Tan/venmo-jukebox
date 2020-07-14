# Venmo Jukebox

This application interfaces between Venmo (through Gmail API in reading payment notifications, we don't ever touch Venmo directly) and Spotify to
queue song requests off Venmo transactions.

**Please note:** This was written for fun and, while functional, is a pain to distribute/get working on any device besides the one I tested on. Might eventually get around to seeing how this could be hosted as a Spotify Developer App/Extension.

## Usage Specifics
Running "python jukebox.py" starts an infinite while loop that detects for new Venmo transactions (through filtered and labeled emails). The content of the "note" in the transaction is what is used to search for songs, and the transaction amount is used to determine how many songs they are allotted (1 nickel = 1 request, so ten cents will look for two requests). A request can either be a song, or "skip" in which the currently playing track is skipped. If multiple requests are included in one note, they need to be separated with either newlines or commas (so don't search for songs with either newlines or commas in the title!)

The device with Spotify needs to be opened and recently active (can be paused or playing).

Refunds are currently not enabled, but the infrastructure is in place to function once Payouts with Venmo API is integrated. We refund if the search feature cannot find the song requested (code for calculation is done), or if the song is skipped (code has not started).

### Example Venmo transactions and behavior:
```
$0.15 - in my life
just the way you are - billy joel
vincent
```
Correctly queues *In My Life* by the Beatles, *Just the Way You Are* by Billy Joel, and *Vincent* by Don McLean. 3 of 3 songs permitted (15 cents = 3 nickels) are found, so no refund is issued.

```
$0.12 - bridge ofer troubled water, i want u back
```
Correctly queues *Bridge Over Troubled Water* by S&G despite the typo, but incorrectly queues *Yours If You Want It* by Rascal Flatts instead of either the Jackson 5 or Cher Lloyd song. Since it has found and queued two songs, it uses up 10 cents and issues 2 cents as a refund.

## Installation

You'll need the packages [Spotipy](https://spotipy.readthedocs.io/en/2.13.0/) (Python wrapper for Spotify API) and the [Gmail Python API library](https://developers.google.com/gmail/api). 

## Setup
Enable [Gmail API](https://developers.google.com/gmail/api/quickstart/python), and save the given credentials.json file into the same folder as jukebox.py.
Set up a filter to label incoming messages from venmo@venmo.com with the content "This payment will be reviewed for compliance with our User Agreement and if we determine that there is a violation by either party, it may be reversed or your ability to transfer to your bank account may be restricted". This should match any payment notification emails from Venmo, but not other emails such as friend requests or security notifications.
![Image of the filter settings](https://github.com/Austin-Tan/venmo-jukebox/blob/master/filter.PNG)


Right now, the Spotify section isn't set up as a single app that many users can connect to hosted on my developer dashboard. To use it, will need to create your own [app here](https://developer.spotify.com/documentation/general/guides/app-settings/#register-your-app) and copy the client ID and secret into the given fields in authentication.py.
Copy Username from your Spotify account into the field in authentication.py.
Add the REDIRECT_URI **from authentication.py into the app on the developer dashboard**.

At this point, you should be able to run:
```python jukebox.py```
where it'll print its actions to the command line and open up web clients to authenticate the application to both Gmail and Spotify. If you uncomment the calls in main() to get_label_ids() and get_device_id(), it'll print the respective information to the command line, and you can fill out the last bits of authentication.py.

A test transaction of $0.05 and a song of your choice while Spotify is open is a good way to test this!


## License
[MIT](https://choosealicense.com/licenses/mit/)
