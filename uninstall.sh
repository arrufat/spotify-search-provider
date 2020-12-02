#!/usr/bin/env bash

set -eu pipefail
cd "$(dirname "$(realpath "${0}")")"

DATADIR=${DATADIR:-/usr/share}
LIBDIR=${LIBDIR:-/usr/lib}

# The actual executable
rm "${LIBDIR}"/spotify-search-provider/spotify-search-provider.py
rmdir "${LIBDIR}"/spotify-search-provider

# Search provider definition
rm "${DATADIR}"/gnome-shell/search-providers/org.gnome.Spotify.SearchProvider.ini

# Desktop file (for having an icon)
rm "${DATADIR}"/applications/org.gnome.Spotify.SearchProvider.desktop

# DBus configuration (no-systemd)
rm "${DATADIR}"/dbus-1/services/org.gnome.Spotify.SearchProvider.service

# DBus configuration (systemd)
rm "${LIBDIR}"/systemd/user/org.gnome.Spotify.SearchProvider.service
