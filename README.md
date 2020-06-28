# Venmo Jukebox

This application interfaces between Venmo (through Gmail API in reading payment notifications, we don't ever touch Venmo directly) and Spotify to
queue song requests off Venmo transactions.

## Installation

You'll need the packages [Spotipy](https://spotipy.readthedocs.io/en/2.13.0/) (Python wrapper for Spotify API) and the [Gmail Python API library](https://developers.google.com/gmail/api). 

```bash
pip install foobar
```

## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)