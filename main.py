import os
import shutil
from time import time
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from tkinter.filedialog import askdirectory
from gui import App

# podaj link do spotify
"""def ask_for_playlist_url():
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
            return url"""


# wskaż lokalizacje do zapisania piosenek
def ask_for_directory():
    location = askdirectory(title='Wybierz Katalog')  # shows dialog box and return the path
    return location


# Zwraca szczegółowe informacje o utworach
def get_tracks_details(url):
    def exception_handling():
        if 'track' in url:
            error_text = "* Nie udało się odnaleść utworu."
            # print("Nie udało się odnaleść utworu.")
        elif 'playlist' in url:
            error_text = "* Nie udało się odnaleść playlisty."
            # print("Nie udało się odnaleść playlisty.")
        elif 'album' in url:
            error_text = "* Nie udało się odnaleść albumu."
            # print("Nie udało się odnaleść albumu.")
        # app.print_error_message(message=error_text)

    # Dane API z Spotify for Developers
    client_id = '21d0ee488daa4a66adbaaaf40c157b40'
    client_secret = 'b3c02482fe9f497d95c9d616f648e642'

    # Inicjalizacja autoryzacji
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = Spotify(client_credentials_manager=client_credentials_manager)

    # Pobieranie informacji o playlisty
    url_id = url.split('/')[-1]
    try:
        if 'track' in url:
            data = sp.track(url_id)
            data_type = 'track'
        elif 'playlist' in url:
            data = sp.playlist_tracks(url_id)
            data_type = 'playlist'
        elif 'album' in url:
            data = [[], []]
            data[0] = sp.album(url_id)['name']  # pobiera nazwe albumu
            data[1] = sp.album_tracks(url_id)
            data_type = 'album'
        return data, data_type
    except Exception as e:
        return exception_handling(), None


# pobiera nowe utwory, te krórych nie ma w playliscie przenosci do "Stare"
def download_and_modify(playlist, lokalizacja, data_type):
    def download(to_download):
        lokalizacja_stare = lokalizacja + '/Stare/'
        os.chdir(lokalizacja)  # zmiana lokalizacji na Spotify

        total = len(to_download)
        if data_type == 'playlist':
            file = open(lokalizacja + '/piosenki.txt', 'w', encoding='utf-8')
        for counter, (track_url, file_name) in enumerate(to_download, start=1):
            print(f'* Pobieranie {counter} z {total}')


            if os.path.isfile(lokalizacja_stare + file_name):  # jeżeli piosenka znajduje się w "Stare" to przeniesie ją zamiast ppbierać
                move_to = lokalizacja + '/' + file_name
                shutil.move(lokalizacja_stare + file_name, move_to)
            else:
                # app.print_status(message=f'* Pobieranie {counter} z {total}')
                os.system(f'spotdl {track_url}')
                if data_type == 'playlist':
                    file.write(f'{track_url}    {file_name}\n')
        if data_type == 'playlist':
            file.close()

    def remove(to_remove):
        if not os.path.exists(lokalizacja+'/Stare'):
            os.mkdir(lokalizacja+'/Stare')

        os.chdir(lokalizacja)  # zmiana lokalizacji na Spotify
        for file in to_remove:
            shutil.move(file, lokalizacja+'/Stare/'+file)

    start_time = time()

    if not os.path.exists(lokalizacja):  # czy katalog istnieje
        os.mkdir(lokalizacja)

    to_remove = []  # zawiera nazwy plików - [file_name, file_name]
    to_download = []  # zawiera link spotify oraz nazwę pliku - [(track_url, file_name)]
    data = []  # autor, tytuł, link aktualnych piosenek w playliście
    if data_type == 'track':
        track_name = playlist['name']
        track_url = playlist['external_urls']['spotify']
        track_author = playlist['artists'][0]['name']
        to_download = [(track_url, f'{track_author} - {track_name}.mp3')]
        return download(to_download)

    elif data_type == 'album':
        if os.listdir(lokalizacja):  # jeżeli we wskazanym katalogu znajdują się już piosenki tworzymy nowy
            album_name = playlist[0]
            lokalizacja += '/'+album_name
            if not os.path.exists(lokalizacja):  # czy katalog istnieje
                os.mkdir(lokalizacja)
        for track in playlist[1]['items']:
            track_name = track['name']
            track_url = track['external_urls']['spotify']
            track_author = track['artists'][0]['name']
            to_download.append((track_url, f'{track_author} - {track_name}.mp3'))
        return download(to_download)

    else:  # data_type == 'playlist'
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

        for track_author, track_name, track_url in data:  # określenie piosenek do pobrania
            if not any(track_url == link[0] for link in old_file):
                to_download.append((track_url, f'{track_author} - {track_name}.mp3'))
        for track_url, track_name in old_file:  # określenie piosenek do usunięcia
            if not any(track_url == link[2] for link in data):
                to_remove.append(track_name + '.mp3')

        remove(to_remove)
        download(to_download)

    end_time = time()
    len_to_remove = len(to_remove)
    len_to_download = len(to_download)

    message = ['', '', '']
    print('-----  PODSUMOWANIE  -----')
    if len_to_download == 0 and len_to_remove == 0:
        print('* Brak zmian.')
        # app.print_status(message='* Brak zmian.')
    else:
        if len_to_download == 0:
            print('* Brak nowych piosenek.')
            message[0] = '* Brak nowych piosenek.'
        elif len_to_download == 1:
            print(f'* Pobrano {len_to_download} nową piosenkę.')
            message[0] = f'* Pobrano {len_to_download} nową piosenkę.'
        elif 1 < len_to_download <= 4:
            print(f'* Pobrano {len_to_download} nowe piosenki.')
            message[0] = f'* Pobrano {len_to_download} nowe piosenki.'
        elif len_to_download >= 5:
            print(f'* Pobrano {len_to_download} nowych piosenek.')
            message[0] = f'* Pobrano {len_to_download} nowych piosenek.'

        if len_to_remove == 1:
            print(f'* Usunięto {len_to_remove} piosenkę.')
            message[1] = f'* Usunięto {len_to_remove} piosenkę.'
        elif 1 < len_to_remove <= 4:
            print(f'* Usunięto {len_to_remove} piosenki.')
            message[1] = f'* Usunięto {len_to_remove} piosenki.'
        elif len_to_remove >= 5:
            print(f'* Usunięto {len_to_remove} piosenek.')
            message[1] = f'* Usunięto {len_to_remove} piosenek.'

        elapsed_time = int(end_time - start_time)
        if elapsed_time < 60:
            display_time = elapsed_time
            print(f"** W czasie: {display_time}s")
            message[2] = f"** W czasie: {display_time}s"
        else:
            if elapsed_time < 3600:
                time_unit = "m"
                display_time = elapsed_time // 60
                seconds = elapsed_time % 60
            else:
                time_unit = "h"
                display_time = elapsed_time // 3600
                seconds = elapsed_time % 3600
            print(f"** W czasie: {display_time}.{seconds}{time_unit}")
            message[2] = f"** W czasie: {display_time}.{seconds}{time_unit}"

        #app.print_status(f'{message[0]}\n{message[1]}\n{message[2]}')


def main(path: str, url: str):  #):  #
    # https://open.spotify.com/playlist/6FS9fW1oI9TKtwnxJtbwRa?si=9585d20479f440f2
    # print(path)
    # print(url)

    # playlist, data_type = get_tracks_details("https://open.spotify.com/album/6yiXkzHvC0OTmhfDQOEWtS")
    # lokalizacja = "D:/Pobrane/spot"
    # print(list(playlist))
    # download_and_modify(playlist, lokalizacja, data_type)

    '''    ^^^ TEST ONLY ^^^    '''
    playlist, data_type = get_tracks_details(url)
    if playlist:
        download_and_modify(playlist, path, data_type)


if __name__ == "__main__":
    # main()
    app = App(ask_for_directory=ask_for_directory, main=main)
    app.mainloop()
