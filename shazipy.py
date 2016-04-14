import sys
import argparse
import bs4
from gmusicapi import Mobileclient
import spotipy
import spotipy.util as util


# service = input("Please enter which music service you want to use: \n (google/spotify) ")

def parse_shazams():
        """Parses shazam history, and returns a list of track dictionaries"""

        file = input("Enter the path to your shazam history html file: ")
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

    api = Mobileclient()
    def login(self):
        # logged_in = False
        email = input("Enter your email for %s: " % service)
        pw = input("Enter your password for %s: " % service)
        logged_in = api.login(email, pw, Mobileclient.FROM_MAC_ADDRESS)
        if logged_in:
            print("Successfuly logged in to Google Play All Access\n")
        else:
            print("Could not login to Google Play All Access, try again\n")
            GooglePlay.login(self)


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

    def choose_update_playlist(song_ids):
        """ Searches user playlists for the desired name.
         Then adds songs to it, or creates a new one."""

        playlist_name = input("Enter a name for the playlist to be created")
        new = False
        playlist_id = ''
        user_pls = api.get_all_user_playlist_contents()
        # Check for existing shazam playlist
        for p in user_pls:
            if p["name"] == playlist_name:
                playlist_id = p['id']
                current_playlist = p                   # current_playlist used to monitor # of tracks
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

    # export SPOTIPY_CLIENT_ID='97473d1466df4eda88729bd53427b16d'
    # export SPOTIPY_CLIENT_SECRET='76c946bdcb044ebc8919df23d37da826'
    # export SPOTIPY_REDIRECT_URI='https://github.com/treethought/shazipy'
    spot = spotipy.Spotify()



    def authorize():

        username = input("Enter your spotify username: ")
        token = util.prompt_for_user_token(username)
        if token:
            print("User authorization successful!\n")
            return token
        else:
            print("authorization failed.")
            return token

    def get_song_id(title, artist):
        """takes in song title and artist as strings and returns Spotify ID or 0 if not found."""
        spot = spotipy.Spotify()
        results = spot.search("flying lotus riot", limit=15,)
        attempt = 0
        res = results['tracks']['items'][attempt]
        # print(res['artists'][0]['name'].lower())
        # print(res['name'].lower())
        # print((res['artists'][0]['name']).lower() == artist.lower())
        # print(res['name'].lower() == title.lower())
        if res['artists'][0]['name'].lower() == artist.lower():
            if res['name'].lower() == title.lower():
                print(res['id'])
                return res['id']
        print("Could not find ID for %s - %s\n" % (title, artist))
        return "0"

    def make_song_id_list(data):
    """Data is a list of track dictionaries. Search AA for each track, and appends nid to a list of ids.
            If track not found, append track dict to failed tracks."""
        song_ids = []
        failed_tracks = []
        for track in data:
            nid = SpotMeths.get_song_id(track["Title"], track["Artist"])
            if nid == "0":
                failed_tracks.append(track)
                pass
            else:
                song_ids.append(nid)
                track["TrackID"] = nid
        print('finished getting song_ids')
        return song_ids

    def choose_update_playlist(song_ids):
        """ Searches user playlists for the desired name.
         Then adds songs to it, or creates a new one."""

        playlist_name = input("Enter a name for the playlist to be created")
        new = False
        playlist_id = ''
        sp = spotipy.Spotify()
        user_playlists = sp.user_playlists()



    










SpotMeths.authorize()
SpotMeths.get_song_id('riot', 'flying lotus')





# def google_main():
#     GooglePlay.login()
#     GooglePlay.data = parse_shazams()
#     GooglePlay.song_ids = make_song_id_list(data)
#     GooglePlay.choose_update_playlist(song_ids)





















