import sys
import argparse
import bs4
from gmusicapi import Mobileclient
import spotipy
import spotipy.util as util
api = Mobileclient()


def parse_shazams():
        """Parses shazam history, and returns a list of track dictionaries"""

        import easygui
        file = easygui.fileopenbox(msg='Select your shazam histor html file', filetypes=['*.html'])
        # file = input("Enter the path to your shazam history html file: ")
        try:
            file = open(file, 'r')
            htmltree = file.read()
            soup = bs4.BeautifulSoup(htmltree, 'html.parser')
            table = soup.find('table')
            table_rows = table.findAll('tr')
            data = []
            for row in table_rows:
                track = {}
                try:
                    cols = row.find_all('td')
                    track["Title"] = cols[0].text.strip()
                    track["TrackID"] = ""
                    track["Artist"] = cols[1].text
                    if not (track in data):
                        data.append(track)
                    print(track)
                except Exception as ex:
                    print(ex)
            print('created list of track dicts')
            return data
        except:
            print('Could not read file. is it html?\n')
            parse_shazams()


class GooglePlay():
    """Methods for google play all access"""

    def login():
        # logged_in = False
        email = input("Enter your gmail")
        pw = input("Enter your gmail password")
        global api
        logged_in = api.login(email, pw, Mobileclient.FROM_MAC_ADDRESS)
        if logged_in:
            print("Successfuly logged in to Google Play All Access\n")
        else:
            print("Could not login to Google Play All Access, try again\n")
            GooglePlay.login()


    def get_song_id(title, artist):
        """takes in song title and artist as strings and returns Google nID or 0 if not found."""

        title = title.lower()
        artist = artist.lower()
        # print("searching %s by %s" % (title, artist))
        results = api.search_all_access(title + " " + artist, max_results=15)
        for item in results["song_hits"]:
            if item["track"]["title"].lower() == title:
                if item["track"]["artist"].lower() == artist:
                    print('ID found for %s - %s' % (artist, title))
                    return item["track"]["nid"]
        print("Could not find ID for %s - %s\n" % (artist, title))
        return "0"

    def make_song_id_list(data):
        """data is a list of track dictionaries. Search AA for each track, and appends nid to a list of ids.
            if track not found, append track dict to failed tracks."""

        song_ids = []
        failed_tracks = []
        for track in data:
            nid = GooglePlay.get_song_id(track["Title"], track["Artist"])
            if nid == "0":
                failed_tracks.append(track)
                pass
            else:
                song_ids.append(nid)
                track["TrackID"] = nid
        print('finished getting song_ids')
        return song_ids

    def choose_update_playlist(song_ids, playlist_name):
        """ Searches user playlists for the desired name.
         Then adds songs to it, or creates a new one."""

        new = False
        playlist_id = ''
        user_pls = api.get_all_user_playlist_contents()
        # Check for existing shazam playlist
        for p in user_pls:
            if p["name"] == playlist_name:
                playlist_id = p['id']
                current_playlist = p                   # current_playlist used to monitor tracks
                print("Found your shazam playlist")    # if limit reached, new playlist is created
                break

        if playlist_id == '':                           # playlist doesnt exist, so create new one
            playlist_id = api.create_playlist(playlist_name)
            print('created new playlist')
            new = True

        if not new:                                     # playlist already exists
            current_tracks = current_playlist["tracks"]
            for track in current_tracks:
                if track["trackId"] in song_ids:
                    song_ids.remove(track["trackId"])   # prevents adding duplicate
            song_ids = filter(None, song_ids)

        for s in song_ids:
            if len(current_playlist['tracks']) < 999:
                api.add_songs_to_playlist(playlist_id, s)  # add to playlist until size limit
                print("added %s" % s)
            else:
                playlist_id = api.create_playlist(playlist_name+"2")
                print('playlist got too large, made a new one')
                api.add_songs_to_playlist(playlist_id, s)
        print('Finished')


class SpotMeths(object):
    """Methods for Spotify"""

    def authorize(username):
        scope = 'playlist-modify-public playlist-modify-private playlist-read-private'
        token = util.prompt_for_user_token(username, scope, '97473d1466df4eda88729bd53427b16d',
                                                            '76c946bdcb044ebc8919df23d37da826',
                                                            'https://github.com/treethought/shazipy')
        if token:
            print("User authorization successful!\n")
            return token
        else:
            print("authorization failed.")
            return SpotMeths.authorize(input("Enter your spotify username: "))

    def get_song_id(title, artist):
        """takes in song title and artist as strings and returns Spotify ID or 0 if not found."""
        sp = spotipy.Spotify()
        try:
            results = sp.search(title + " " + artist, limit=15)
            if results['tracks']['total'] > 0:
                attempt = 0
                for result in results:
                    res = results['tracks']['items'][attempt]
                    if res['artists'][0]['name'].lower() == artist.lower():
                        if res['name'].lower() == title.lower():
                            print('Found ID for %s - %s\n' % (title, artist))
                            return res['id']
                    print("Could not find ID for %s - %s\n" % (title, artist))
                    return "0"
            else:
                print('No results for %s - %s\n' % (title, artist))
                return '0'
        except Exception as e:
            print(e)
            return '0'

    def make_song_id_list(data):
        """Data is a list of track dictionaries. Search AA for each track, and appends nid to a list of ids.
            If track not found, append track dict to failed tracks."""
        song_ids = []
        failed_tracks = []
        for track in data:
            nid = SpotMeths.get_song_id(track["Title"], track["Artist"])
            if nid == "0":
                failed_tracks.append(track)
            else:
                song_ids.append(nid)
                track["TrackID"] = nid
        print('Finished getting song_ids\n')
        print("Couldn't find id for the following tracks:\n")
        for track in failed_tracks:
            print('%s - %s' % (track["Title"], track["Artist"]))
        return song_ids

    def choose_update_playlist(username, song_ids, playlist_name, token):
        """ Searches user playlists for the desired name.
         Then adds songs to it, or creates a new one."""

        # scope = 'playlist-modify-public playlist-modify-private playlist-read-private'
        # token = util.prompt_for_user_token(username, scope)
        # if token:
        new = False
        playlist_id = ''
        sp = spotipy.Spotify(auth=token)
        user_playlists = sp.user_playlists(username)
        for p in user_playlists['items']:
            # print(p['name'])
            if p['name'] == playlist_name:
                # current_playlist = p
                playlist_id = p['id']
                print(playlist_id)
                print("Found your shazam playlist with ID: %s" % playlist_id)
                break

        if playlist_id == '':                                # playlist_name not found, create one
            newplaylist = (sp.user_playlist_create(username, playlist_name))
            playlist_id = newplaylist['id']
            print('created new playlist')
            new = True

        if not new:                               # prevent duplicates, by removing existing songs
            contents = sp.user_playlist(username, playlist_id, fields="tracks")
            # pprint(contents['tracks']['items'])
            for item in contents['tracks']['items']:
                if item['track']['id'] in song_ids:
                    song_ids.remove(item['track']['id'])   # prevents adding duplicate
            song_ids = filter(None, song_ids)

        try:
            sp.user_playlist_add_tracks(username, playlist_id, song_ids)
            print('Finished')
        except Exception as e:
            print(e)


def spotify_main(playlist_name):
    username = input("Enter your spotify username: ")
    token = SpotMeths.authorize(username)
    data = parse_shazams()
    song_ids = SpotMeths.make_song_id_list(data)
    SpotMeths.choose_update_playlist(username, song_ids, playlist_name, token)


def google_main(playlist_name):
    GooglePlay.login()
    data = parse_shazams()
    song_ids = GooglePlay.make_song_id_list(data)
    GooglePlay.choose_update_playlist(song_ids, playlist_name)


def main():
    playlist_name = input("Enter a name for the playlist to be created: ")
    service = input("Please enter which music service you want to use: \n (google/spotify) ")
    if service == "g" or service == 'google':
        google_main(playlist_name)
    else:
        spotify_main(playlist_name)

main()
