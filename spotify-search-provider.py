#!/usr/bin/env python3

import os
import sys
from urllib.request import urlopen

import dbus
import dbus.service

from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from spotipy import Spotify, SpotifyPKCE


search_bus_name = "org.gnome.Shell.SearchProvider2"
sbn = dict(dbus_interface=search_bus_name)

CLIENT_ID = "9226139be2064e9890c50b8021bbbfbf"
CACHE_DIR = os.path.expanduser("~/.cache/spotify-search-provider/")
ALBUMART_DIR = os.path.join(CACHE_DIR, "albumart")
CACHE_FILE = os.path.join(CACHE_DIR, ".cache")
REDIRECT_URI = "http://localhost:5071/callback"
ACCESS_SCOPE = "user-modify-playback-state user-read-playback-state"

search_bus_name = "org.gnome.Shell.SearchProvider2"
sbn = dict(dbus_interface=search_bus_name)


def debug(s):
    print("\n### DEBUG ###\n%s\n### DEBUG ###\n" % s, file=sys.stderr)


def parse_tracks(raw):
    out = []
    for track in raw["tracks"]["items"]:
        track_details = dict(
            title=track["name"],
            artist=track["album"]["artists"][0]["name"],
            album=track["album"]["name"],
            uri=track["uri"],
            albumart_url=track["album"]["images"][-1]["url"],
        )
        out.append(track_details)
    if not out:
        out.append(dict(uri="", title="", artist="", album=""))
    return out


class SpotifySearchProvider(dbus.service.Object):
    """The Spotify Search daemon."""

    bus_name = "org.gnome.Spotify.SearchProvider"
    _object_path = "/" + bus_name.replace(".", "/")

    def __init__(self):
        self.results = []
        self.session_bus = dbus.SessionBus()
        self.command = None
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)
        os.makedirs(ALBUMART_DIR, exist_ok=True)

        self.auth_manager = SpotifyPKCE(
            client_id=CLIENT_ID,
            cache_path=CACHE_FILE,
            redirect_uri=REDIRECT_URI,
            scope=ACCESS_SCOPE,
        )

        self.spotify = Spotify(auth_manager=self.auth_manager)

    @dbus.service.method(in_signature="sasu", **sbn)
    def ActivateResult(self, id, terms, timestamp):
        debug(terms)
        cmd = terms[0][1:]
        if cmd == "":  # queue by default
            cmd = "queue"
        debug(cmd)
        msg = None
        if cmd == "play":
            self.spotify.start_playback(uris=[id])
            msg = "Now playing"
        elif cmd == "queue" or cmd == "q":
            self.spotify.add_to_queue(uri=id)
            msg = "Added to queue"
        else:
            self.notify("Unknown Command", body=cmd)
            return

        self.notify(
            msg,
            body=self.results[id]["artist"] + " - " + self.results[id]["title"],
            icon=self.results[id]["icon"],
        )

    @dbus.service.method(in_signature="as", out_signature="as", **sbn)
    def GetInitialResultSet(self, terms):
        # only parse queries that start with $ and contain 2 or more terms
        if not terms[0].startswith("$"):
            return []
        if len(terms) < 2:
            return []
        qs = ""
        for q in terms[1:]:
            qs += q + " "
        qs.strip()
        if len(qs) < 2:
            return []

        out = []
        self.results = {}
        tracks = parse_tracks(self.spotify.search(qs, limit=5))
        for track in tracks:
            self.results[track["uri"]] = {
                "title": track["title"],
                "artist": track["artist"],
                "album": track["album"],
                "albumart_url": track["albumart_url"],
            }
            out.append(track["uri"])
        return out

    @dbus.service.method(in_signature="asas", out_signature="as", **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        return self.GetInitialResultSet(new_terms)

    @dbus.service.method(in_signature="as", out_signature="aa{sv}", **sbn)
    def GetResultMetas(self, ids):
        out = []
        for uri in ids:
            if uri in self.results:
                entry = {}
                entry["id"] = uri
                entry["name"] = self.results[uri]["title"]
                entry["description"] = (
                    self.results[uri]["artist"] + " - " + self.results[uri]["album"]
                )
                basename = os.path.basename(self.results[uri]["albumart_url"])
                albumart_path = os.path.join(ALBUMART_DIR, basename)
                if not os.path.exists(albumart_path):
                    with open(albumart_path, "wb") as f:
                        with urlopen(self.results[uri]["albumart_url"]) as r:
                            f.write(r.read())
                self.results[uri]["icon"] = albumart_path
                entry["gicon"] = albumart_path
                out.append(entry)
        return out

    @dbus.service.method(in_signature="asu", terms="as", timestamp="u", **sbn)
    def LaunchSearch(self, terms, timestamp):
        pass

    def notify(self, message, body="", icon="spotify-client", error=False):
        try:
            self.session_bus.get_object(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
            ).Notify(
                "Spotify",
                0,
                icon,
                message,
                body,
                "",
                {"transient": False if error else True},
                0 if error else 3000,
                dbus_interface="org.freedesktop.Notifications",
            )
        except dbus.DBusException as err:
            print(f"Error {err} while trying to display {message}.")


if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)
    SpotifySearchProvider()
    GLib.MainLoop().run()
