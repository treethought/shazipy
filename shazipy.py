import bs4
from gmusicapi import Mobileclient
api = Mobileclient()

file = 
gmail = 
pw = 


def glogin(gmail, pw):
    logged_in = api.login(gmail, pw, Mobileclient.FROM_MAC_ADDRESS)
    print('logged in')
    return logged_in


def create_list(file):
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
            print track
        except Exception as ex:
            print(ex)
    print('created list of track dics')
    return data


def search_song(title, artist):
    title = title.lower()
    artist = artist.lower()
    # print("searching %s by %s" % (title, artist))
    results = api.search_all_access(title + " " + artist, max_results=15)
    for item in results["song_hits"]:
        if item["track"]["title"].lower() == title:
            if item["track"]["artist"].lower() == artist:
                return item["track"]["nid"]
    print('done searching for songs')
    return "0"


def get_song_ids(data):
    song_ids = []
    for track in data:
        nid = search_song(track["Title"], track["Artist"])
        if nid == "0":
            pass
        else:
            song_ids.append(nid)
            track["TrackID"] = nid
    print('finished getting song_ids')
    return song_ids


def choose_update_playlist(song_ids, playlist_name):
    new = False
    pl_id = ''
    user_pls = api.get_all_user_playlist_contents()
    # Check for existing shazam playlist
    for p in user_pls:
        if p["name"] == playlist_name:
            pl_id = p['id']
            current_pl = p
            print ("Found your shazam playlist")
            break
    if pl_id == '':
        pl_id = api.create_playlist(playlist_name)
        print('created new playlist')
        new = True

    if not new:
        current_tracks = current_pl["tracks"]
        for track in current_tracks:
            if track["trackId"] in song_ids:
                song_ids.remove(track["trackId"])
        song_ids = filter(None, song_ids)
    # print(song_ids)
    for s in song_ids:
        if len(current_pl['tracks']) < 999:
            api.add_songs_to_playlist(pl_id, s)
            print ("added %s" % s)
        else:
            pl_id = api.create_playlist(playlist_name+"2")
            print ('playlist got too large, made a new one')
            api.add_songs_to_playlist(pl_id, s)
    print ('Finished')

glogin(gmail, pw)
data = create_list(file)
song_ids = get_song_ids(data)
choose_update_playlist(song_ids, 'Halies-Shazams')




# for p in api.get_all_user_playlist_contents():
#     print (len(p['tracks']))



















