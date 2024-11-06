# spotify-search-provider
Spotify search provider for GNOME Shell

![Screencast](misc/screencast.gif)

## Installation

### Arch Linux

Install [`spotify-search-provider`](https://aur.archlinux.org/packages/spotify-search-provider/) from the [AUR](https://aur.archlinux.org/):

```
yay -S spotify-search-provider
```

### Manual

Install the following dependencies:

- python-dbus (might be named python3-dbus)
- python-gobject (might be named python3-gobject)
- [spotipy](https://github.com/plamere/spotipy): `pip install --user spotipy`

Then run:
``` bash
git clone https://github.com/arrufat/spotify-search-provider
cd spotify-search-provider
sudo ./install.sh
```

And to uninstall it:
``` bash
sudo ./uninstall.sh
```

## Credits

- [gnome-pass-search-provider](https://github.com/jle64/gnome-pass-search-provider)
- [krunner-spotify](https://github.com/MartijnVogelaar/krunner-spotify)
