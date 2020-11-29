#!/usr/bin/env python3

import os
import sys

import dbus
import dbus.service

from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from spotipy import Spotify, SpotifyPKCE

search_bus_name = "org.gnome.Shell.SearchProvider2"
sbn = dict(dbus_interface=search_bus_name)

CLIENT_ID = "9226139be2064e9890c50b8021bbbfbf"
CACHE_PATH = os.path.expanduser("~/.cache/gssp-spotify/.cache")
REDIRECT_URI = "http://localhost:8888/callback"
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
            # albumart_url=track["album"]["images"][-1]["url"],
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
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        self.auth_manager = SpotifyPKCE(
            client_id=CLIENT_ID,
            cache_path=CACHE_PATH,
            redirect_uri=REDIRECT_URI,
            scope=ACCESS_SCOPE,
        )

        self.spotify = Spotify(auth_manager=self.auth_manager)
        self.spotify.current_user()

    @dbus.service.method(in_signature="sasu", **sbn)
    def ActivateResult(self, id, terms, timestamp):
        self.spotify.start_playback(uris=[id])

    @dbus.service.method(in_signature="as", out_signature="as", **sbn)
    def GetInitialResultSet(self, terms):
        qs = ""
        for q in terms:
            qs += q + " "
        qs.strip()
        if len(qs) < 2:
            return []

        out = []
        self.results = {}
        tracks = parse_tracks(self.spotify.search("artist:" + qs))
        for track in tracks:
            self.results[track["uri"]] = {
                "title": track["title"],
                "artist": track["artist"],
                "album": track["album"],
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
                entry["gicon"] = "spotify-client"
                out.append(entry)
        return out

    @dbus.service.method(in_signature="asu", terms="as", timestamp="u", **sbn)
    def LaunchSearch(self, terms, timestamp):
        pass


if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)
    SpotifySearchProvider()
    GLib.MainLoop().run()
