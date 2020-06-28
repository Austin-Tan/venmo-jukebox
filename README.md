# Venmo Jukebox

This application interfaces between Venmo (through Gmail API in reading payment notifications, we don't ever touch Venmo directly) and Spotify to
queue song requests off Venmo transactions.

## Usage Specifics
Running "python jukebox.py" starts an infinite while loop that detects for new Venmo transactions (through filtered and labeled emails). The content of the "note" in the transaction is what is used to search for songs, and the transaction amount is used to determine how many songs they are allotted (1 nickel = 1 request, so ten cents will look for two requests). A request can either be a song, or "skip" in which the currently playing track is skipped. If multiple requests are included in one note, they need to be separated with either newlines or commas (so don't search for songs with either newlines or commas in the title!)

The device with Spotify needs to be opened and recently active (can be paused or playing).

Refunds are currently not enabled, but the infrastructure is in place to function once Payouts with Venmo API is integrated. We refund if the search feature cannot find the song requested (code for calculation is done), or if the song is skipped (code has not started).

### Example transactions and behavior:
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
Fill in authentication.py with the client information for the Gmail account which receives your Venmo payment notifications, and the client information for your Spotify account.

## License
[MIT](https://choosealicense.com/licenses/mit/)
