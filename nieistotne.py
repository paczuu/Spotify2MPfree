from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont


# tworzy pdf z tabel� zawieraj�c� lp., autor, nazwa utworu, link do utworu
def create_pdf(playlist):

    '''data = [['Lp.', 'Autor', 'Tytu�', 'URL']]  # autor, tytu�, link aktualnych piosenek w playli�cie
    for idx, track in enumerate(playlist['items'], start=1):
        track_name = track['track']['name']
        track_url = track['track']['external_urls']['spotify']
        track_author = track['track']['artists'][0]['name']
        data.append([track_author, track_name, track_url])'''

    # Tworzenie pliku PDF
    pdf_filename = 'playlist_info.pdf'
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)

    # Tworzenie danych do tabeli
    table_data = [['Lp.', 'Autorzy', 'Tytu�', 'URL']]
    for idx, track in enumerate(playlist['items'], start=1):
        track_name = track['track']['name']
        track_url = track['track']['external_urls']['spotify']
        track_artists = ', '.join([artist['name'] for artist in track['track']['artists']])
        table_data.append([idx, track_artists, track_name, track_url])

    # Ustal szeroko�� strony
    page_width, page_height = letter
    table_width = page_width

    # Tworzenie tabeli
    table = Table(table_data, colWidths=[30, 150, 150, 200])

    # Ustalanie szeroko�ci tabeli
    table._argW[0] = table_width * 0.05  # Szeroko�� pierwszej kolumny
    table._argW[1] = table_width * 0.3  # Szeroko�� drugiej kolumny
    table._argW[2] = table_width * 0.3  # Szeroko�� trzeciej kolumny
    table._argW[3] = table_width * 0.35  # Szeroko�� czwartej kolumny

    # Dodawanie czcionki Arial do dokumentu PDF
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))  # Podaj pe�n� �cie�k� do pliku czcionki Arial

    # Stylizacja tabeli
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Arial'),  # Ustawienie czcionki na Arial
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Linie oddzielaj�ce kom�rki
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Wyr�wnanie tekstu do �rodka kom�rek
        ('WORDWRAP', (0, 1), (-1, -1)),  # Zawijanie tekstu od drugiego wiersza
    ])

    table.setStyle(style)

    # Dodawanie tabeli do dokumentu PDF
    doc.build([table])

    print(f'Plik PDF zosta� utworzony: {pdf_filename}')