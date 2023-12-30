import os
import time
import shutil
from getpass import getuser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tkinter.filedialog import askdirectory
from gui import App

# podaj link do spotify
def ask_for_playlist_url():
    while True:
        # url = str(input("Wklej adres url playlisty/ albumu spotify: "))
        # url = 'https://open.spotify.com/track/0E0kxko3i9b5JxxMoGH3At?si=9e5e9349da954dee'  # track
        # url = 'https://open.spotify.com/playlist/73WF2YDYoyIjFNnHE7SMK9'  # playlist
        # url = 'https://open.spotify.com/album/6yiXkzHvC0OTmhfDQOEWtS'  # album
        url = 'https://open.spotify.com/playlist/6FS9fW1oI9TKtwnxJtbwRa?si=9585d20479f440f2'  # test playlist

        if 'https://open.spotify.com/track/' in url or \
            'https://open.spotify.com/playlist/' in url or \
            'https://open.spotify.com/album/' in url:
            if '?' in url:
                url = url.split('?')[0]
            return url


# pobiera systemową lokalizację folderu Muzyka w Windows
def get_music_folder_path():
    current_user = getuser()
    music_folder_path = f'C:/Users/{current_user}/Music/Spotify'

    return music_folder_path


# wskaż lokalizacje do zapisania piosenek
def ask_for_directory():
    location = askdirectory(title='Wybierz Katalog')  # shows dialog box and return the path
    return location

# Zwraca szczegółowe informacje o utworach
def get_tracks_details(url):
    # Dane API z Spotify for Developers
    client_id = '21d0ee488daa4a66adbaaaf40c157b40'
    client_secret = 'b3c02482fe9f497d95c9d616f648e642'

    # Inicjalizacja autoryzacji
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Pobieranie informacji o playlisty
    url_id = url.split('/')[-1]
    try:
        if 'track' in url:
            data = sp.track(url_id)
            print(data)
        elif 'playlist' in url:
            data = sp.playlist_tracks(url_id)
        elif 'album' in url:
            data = sp.album_tracks(url_id)
        return data
    except Exception as e:
        if 'track' in url:
            error_text = "* Nie udało się odnaleść utworu."
            # print("Nie udało się odnaleść utworu.")
        elif 'playlist' in url:
            error_text = "* Nie udało się odnaleść playlisty."
            # print("Nie udało się odnaleść playlisty.")
        elif 'album' in url:
            error_text = "* Nie udało się odnaleść albumu."
            # print("Nie udało się odnaleść albumu.")
        app.print_error_message(message=error_text)
        # return ask_for_playlist_url()


# pobiera nowe utwory, te krórych nie ma w playliscie przenosci do "Stare"
def download_and_modify(playlist, lokalizacja):
    def download(to_download):
        lokalizacja_stare = lokalizacja + '/Stare/'
        os.chdir(lokalizacja)  # zmiana lokalizacji na Spotify

        total = len(to_download)
        for counter, (track_url, file_name) in enumerate(to_download, start=1):
            print(f'* Pobieranie {counter} z {total}')
            if os.path.isfile(lokalizacja_stare + file_name):  # jeżeli piosenka znajduje się w "Stare" to przeniesie ją zamiast ppbierać
                move_to = lokalizacja + '/' + file_name
                shutil.move(lokalizacja_stare + file_name, move_to)
            else:
                os.system(f'spotdl {track_url}')

    def remove(to_remove):
        if not os.path.exists(lokalizacja+'/Stare'):
            os.mkdir(lokalizacja+'/Stare')

        os.chdir(lokalizacja)  # zmiana lokalizacji na Spotify
        for file in to_remove:
            shutil.move(file, os.path.join(lokalizacja+'/Stare/', file))

    start_time = time.time()

    if not os.path.exists(lokalizacja):  # czy katalog istnieje
        os.mkdir(lokalizacja)

    to_remove = []  # zawiera nazwy plików - [file_name, file_name]
    to_download = []  # zawiera link spotify oraz nazwę pliku - [(track_url, file_name)]
    data = []  # autor, tytuł, link aktualnych piosenek w playliście
    for track in playlist['items']:
        track_name = track['track']['name']
        track_url = track['track']['external_urls']['spotify']
        track_author = track['track']['artists'][0]['name']
        data.append([track_author, track_name, track_url])

    if not os.path.isfile(lokalizacja+'/piosenki.txt'):  # jeśli lista nie istnieje pobiera wszystkie utwory
        file = open(lokalizacja+'/piosenki.txt', 'x', encoding='utf-8')

        for track_author, track_name, track_url in data:
            to_download.append((track_url, f'{track_author} - {track_name}.mp3'))
            file.write(f'{track_url}    {track_author} - {track_name}\n')
        file.close()
        download(to_download)
    else:
        old_file = open(lokalizacja+'/piosenki.txt', 'r', encoding='utf-8')
        old_file = [line.strip() for line in old_file.readlines()]  # dzielenie na linie
        old_file = [line.split('    ') for line in old_file]  # dzielenie na url i tytuł
        file = open(lokalizacja+'/piosenki.txt', 'w', encoding='utf-8')

        for track_author, track_name, track_url in data:  # wspisanie aktualnego stanu piosenek do listy
            file.write(f'{track_url}    {track_author} - {track_name}\n')
        file.close()

        for track_author, track_name, track_url in data:  # określenie piosenek do pobrania
            if not any(track_url == link[0] for link in old_file):
                to_download.append((track_url, f'{track_author} - {track_name}.mp3'))
        for track_url, track_name in old_file:  # określenie piosenek do usunięcia
            if not any(track_url == link[2] for link in data):
                to_remove.append(track_name + '.mp3')

        remove(to_remove)
        download(to_download)

    end_time = time.time()
    len_to_remove = len(to_remove)
    len_to_download = len(to_download)

    print('-----  PODSUMOWANIE  -----')
    if len_to_download == 0 and len_to_remove == 0:
        print('* Brak zmian.')
    else:
        if len_to_download == 0:
            print('* Brak nowych piosenek.')
        elif len_to_download == 1:
            print(f'* Pobrano {len_to_download} nową piosenkę.')
        elif 1 < len_to_download <= 4:
            print(f'* Pobrano {len_to_download} nowe piosenki.')
        elif len_to_download >= 5:
            print(f'* Pobrano {len_to_download} nowych piosenek.')

        if len_to_remove == 1:
            print(f'* Usunięto {len_to_remove} piosenkę.')
        elif 1 < len_to_remove <= 4:
            print(f'* Usunięto {len_to_remove} piosenki.')
        elif len_to_remove >= 5:
            print(f'* Usunięto {len_to_remove} piosenek.')

        elapsed_time = end_time - start_time
        if elapsed_time < 60:
            time_unit = "s"
            display_time = elapsed_time
            print(f"** W czasie: {display_time:.0f}{time_unit}")
        else:
            if elapsed_time < 3600:
                time_unit = "m"
                display_time = elapsed_time / 60
            else:
                time_unit = "h"
                display_time = elapsed_time / 3600
            print(f"** W czasie: {display_time:.2f}{time_unit}")


def main(path: str, url: str):
    # https://open.spotify.com/playlist/6FS9fW1oI9TKtwnxJtbwRa?si=9585d20479f440f2
    print(path)
    print(url)
    '''    ^^^ TEST ONLY ^^^    '''
    playlist = get_tracks_details(url)
    download_and_modify(playlist, path)


if __name__ == "__main__":
    app = App(get_music_folder_path=get_music_folder_path, ask_for_directory=ask_for_directory, main=main)
    app.mainloop()
