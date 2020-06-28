# Venmo Jukebox

This application interfaces between Venmo (through Gmail API in reading payment notifications, we don't ever touch Venmo directly) and Spotify to
queue song requests off Venmo transactions.

## Installation

You'll need the packages [Spotipy](https://spotipy.readthedocs.io/en/2.13.0/) (Python wrapper for Spotify API) and the [Gmail Python API library](https://developers.google.com/gmail/api). 

Fill in authentication.py with the client information for the Gmail account which receives your Venmo payment notifications, and the client information for your Spotify account (more details to come).

## License
[MIT](https://choosealicense.com/licenses/mit/)