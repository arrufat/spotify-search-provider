#!/usr/bin/env bash

set -eu pipefail
cd "$(dirname "$(realpath "${0}")")"

DATADIR=${DATADIR:-/usr/share}
LIBDIR=${LIBDIR:-/usr/lib}

# The actual executable
install -Dm 0755 spotify-search-provider.py "${LIBDIR}"/spotify-search-provider/spotify-search-provider.py

# Search provider definition
install -Dm 0644 conf/org.gnome.Spotify.SearchProvider.ini "${DATADIR}"/gnome-shell/search-providers/org.gnome.Spotify.SearchProvider.ini

# Desktop file (for having an icon)
install -Dm 0644 conf/org.gnome.Spotify.SearchProvider.desktop "${DATADIR}"/applications/org.gnome.Spotify.SearchProvider.desktop

# DBus configuration (no-systemd)
install -Dm 0644 conf/org.gnome.Spotify.SearchProvider.service.dbus "${DATADIR}"/dbus-1/services/org.gnome.Spotify.SearchProvider.service

# DBus configuration (systemd)
install -Dm 0644 conf/org.gnome.Spotify.SearchProvider.service.systemd "${LIBDIR}"/systemd/user/org.gnome.Spotify.SearchProvider.service
