import os
import time
import shutil
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont


# podaj link do spotify
def ask_for_playlist_url():
    while True:
        #url = str(input("Wklej adres url playlisty/ albumu spotify: "))
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


# wskaż lokalizacje do zapisania piosenek
def ask_for_directory():
    pass

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
            print("Nie udało się odnaleść utworu.")
        elif 'playlist' in url:
            print("Nie udało się odnaleść playlisty.")
        elif 'album' in url:
            print("Nie udało się odnaleść albumu.")
        return ask_for_playlist_url()


# tworzy pdf z tabelą zawierającą lp., autor, nazwa utworu, link do utworu
def create_pdf(playlist):

    '''data = [['Lp.', 'Autor', 'Tytuł', 'URL']]  # autor, tytuł, link aktualnych piosenek w playliście
    for idx, track in enumerate(playlist['items'], start=1):
        track_name = track['track']['name']
        track_url = track['track']['external_urls']['spotify']
        track_author = track['track']['artists'][0]['name']
        data.append([track_author, track_name, track_url])'''

    # Tworzenie pliku PDF
    pdf_filename = 'playlist_info.pdf'
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)

    # Tworzenie danych do tabeli
    table_data = [['Lp.', 'Autorzy', 'Tytuł', 'URL']]
    for idx, track in enumerate(playlist['items'], start=1):
        track_name = track['track']['name']
        track_url = track['track']['external_urls']['spotify']
        track_artists = ', '.join([artist['name'] for artist in track['track']['artists']])
        table_data.append([idx, track_artists, track_name, track_url])

    # Ustal szerokość strony
    page_width, page_height = letter
    table_width = page_width

    # Tworzenie tabeli
    table = Table(table_data, colWidths=[30, 150, 150, 200])

    # Ustalanie szerokości tabeli
    table._argW[0] = table_width * 0.05  # Szerokość pierwszej kolumny
    table._argW[1] = table_width * 0.3  # Szerokość drugiej kolumny
    table._argW[2] = table_width * 0.3  # Szerokość trzeciej kolumny
    table._argW[3] = table_width * 0.35  # Szerokość czwartej kolumny

    # Dodawanie czcionki Arial do dokumentu PDF
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))  # Podaj pełną ścieżkę do pliku czcionki Arial

    # Stylizacja tabeli
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Arial'),  # Ustawienie czcionki na Arial
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Linie oddzielające komórki
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Wyrównanie tekstu do środka komórek
        ('WORDWRAP', (0, 1), (-1, -1)),  # Zawijanie tekstu od drugiego wiersza
    ])

    table.setStyle(style)

    # Dodawanie tabeli do dokumentu PDF
    doc.build([table])

    print(f'Plik PDF został utworzony: {pdf_filename}')


# pobiera nowe utwory, te krórych nie ma w playliscie przenosci do "Stare"
def download_and_modify(playlist, lokalizacja):
    def download(to_download):
        lokalizacja_stare = lokalizacja + 'Spotify/Stare/'
        os.chdir(lokalizacja + 'Spotify')  # zmiana lokalizacji na Spotify

        total = len(to_download)
        for counter, (track_url, file_name) in enumerate(to_download, start=1):
            print(f'* Pobieranie {counter} z {total}')
            if os.path.isfile(lokalizacja_stare + file_name):  # jeżeli piosenka znajduje się w "Stare" to przeniesie ją zamiast ppbierać
                move_to = lokalizacja + 'Spotify/' + file_name
                shutil.move(lokalizacja_stare + file_name, move_to)
            else:
                os.system(f'spotdl {track_url}')

    def remove(to_remove):
        if not os.path.exists(lokalizacja+'Spotify/Stare'):
            os.mkdir(lokalizacja+'Spotify/Stare')

        os.chdir(lokalizacja+'Spotify')  # zmiana lokalizacji na Spotify
        for file in to_remove:
            shutil.move(file, os.path.join(lokalizacja+'Spotify/Stare/', file))


    start_time = time.time()
    if not os.path.exists(lokalizacja+'Spotify'):  # czy katalog istnieje
        os.mkdir(lokalizacja+'Spotify')

    to_remove = []  # zawiera nazwy plików - [file_name, file_name]
    to_download = []  # zawiera link spotify oraz nazwę pliku - [(track_url, file_name)]
    data = []  # autor, tytuł, link aktualnych piosenek w playliście
    for track in playlist['items']:
        track_name = track['track']['name']
        track_url = track['track']['external_urls']['spotify']
        track_author = track['track']['artists'][0]['name']
        data.append([track_author, track_name, track_url])

    if not os.path.isfile(lokalizacja+'Spotify/piosenki.txt'):  # jeśli lista nie istnieje pobiera wszystkie utwory
        file = open(lokalizacja+'Spotify/piosenki.txt', 'x', encoding='utf-8')

        for track_author, track_name, track_url in data:
            to_download.append((track_url, f'{track_author} - {track_name}.mp3'))
            file.write(f'{track_url}    {track_author} - {track_name}\n')
        file.close()
        download(to_download)
    else:
        old_file = open(lokalizacja+'Spotify/piosenki.txt', 'r', encoding='utf-8')
        old_file = [line.strip() for line in old_file.readlines()]  # dzielenie na linie
        old_file = [line.split('    ') for line in old_file]  # dzielenie na url i tytuł
        file = open(lokalizacja+'Spotify/piosenki.txt', 'w', encoding='utf-8')

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


def main():
    lokalizacja = 'D:/Programy/PyCharm 2023.2.3/Projekty/Spotify2MPfree/'  # w formacie 'X:/**/**/'
    url = ask_for_playlist_url()
    playlist = get_tracks_details(url)

    download_and_modify(playlist, lokalizacja)

    # create_pdf(playlist)


if __name__ == "__main__":
    main()