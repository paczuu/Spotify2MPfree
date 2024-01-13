import tkinter.messagebox
import customtkinter as ctk
# from main import ask_for_directory, main
from os.path import isdir
from re import match
from getpass import getuser

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self, ask_for_directory, main):
        super().__init__()
        self.ask_for_directory = ask_for_directory
        self.main = main
        self.location = self.get_music_folder_path()


        # configure window
        self.title("Spotify2MPfree")
        self.geometry(f"{630}x{300}")
        self.resizable(False, False)

        # configure grid layout (5r x 3c)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        '''
                Ask for location
        '''
        self.textbox = ctk.CTkTextbox(master=self,
                                      width=400,
                                      corner_radius=0,
                                      fg_color='transparent',
                                      text_color='white')
        self.textbox.grid(row=0, column=0, padx=(15, 0), pady=(10, 20), sticky="n")
        self.textbox.insert("0.0", "* Katalog z utworami:")

        self.entry_location = ctk.CTkEntry(self,
                                           placeholder_text=self.location,
                                           placeholder_text_color='black',
                                           text_color='black',
                                           fg_color='#9c9c9c',
                                           border_color='#575757',
                                           border_width=2,
                                           corner_radius=20)
        self.entry_location.grid(row=0, column=0, columnspan=2, padx=(20, 0), pady=(33, 20), sticky="new")

        self.button_location = ctk.CTkButton(master=self,
                                             fg_color="#9c9c9c",
                                             text_color='black',
                                             border_width=2,
                                             border_color='#575757',
                                             corner_radius=20,
                                             text="Zmien",
                                             hover=True,
                                             hover_color='#dedede',
                                             command=self.change_placeholder_text)  # zmiana lokalizacji
        self.button_location.grid(row=0, column=2, padx=(10, 0), pady=(33, 20), sticky="nw")

        '''
                Choose action
        '''
        # create radiobutton frame
        self.radiobutton_frame = ctk.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, rowspan=3, column=3, padx=(20, 20), pady=(30, 20), sticky="nsew")
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = ctk.CTkLabel(master=self.radiobutton_frame,
                                              text="Wybierz dzialanie:")
        self.label_radio_group.grid(row=0, column=3, columnspan=1, padx=10, pady=15, sticky="")
        self.radio_button_1 = ctk.CTkRadioButton(master=self.radiobutton_frame,
                                                 variable=self.radio_var,
                                                 value=0,
                                                 text='Aktualizuj',
                                                 height=30)
        self.radio_button_1.grid(row=1, column=3, pady=10, padx=20, sticky="n")
        self.radio_button_2 = ctk.CTkRadioButton(master=self.radiobutton_frame,
                                                 variable=self.radio_var,
                                                 value=1,
                                                 text='Pobierz',
                                                 height=30)
        self.radio_button_2.grid(row=2, column=3, pady=10, padx=20, sticky="n")

        '''
                Summary/ important info ------------------------------------------------------------------ - - - - - -- - -- - - -
        '''
        self.textbox_status = ctk.CTkTextbox(self)
        self.textbox_status = ctk.CTkTextbox(master=self,
                                             width=400,
                                             height=50,
                                             corner_radius=0,
                                             fg_color='transparent',
                                             bg_color='transparent')
        self.textbox_status.grid(row=0, rowspan=2, column=0, columnspan=2, padx=(15, 0), pady=(70, 20), sticky="nws")

        '''
                Bottom row (url + execute)
        '''
        # create url entry and button
        self.entry_url = ctk.CTkEntry(self,
                                      placeholder_text="Wpisz url...",
                                      placeholder_text_color='black',
                                      text_color='black',
                                      fg_color='#9c9c9c',
                                      border_color='#575757',
                                      border_width=2,
                                      corner_radius=20)
        self.entry_url.grid(row=4, column=0, columnspan=3, padx=(20, 0), pady=(10, 20), sticky="nsew")

        self.button_proceed = ctk.CTkButton(master=self,
                                            fg_color="#9c9c9c",
                                            text_color='black',
                                            border_width=2,
                                            border_color='#575757',
                                            corner_radius=20,
                                            text="Kontynuuj",
                                            hover=True,
                                            hover_color='#dedede',
                                            command=self.get_entry_text)  # skoñczyæ
        # command=self.download_and_modify)  # wykonaj program
        self.button_proceed.grid(row=4, column=3, padx=(20, 20), pady=(10, 20), sticky="nsew")

    def get_entry_text(self):
        url = self.entry_url.get()
        temp_loc = self.entry_location.get()
        correct_url = False
        correct_location = True

        if temp_loc:   # czy wpisana lokalizacja jest porawna, jest nie wpisano weŸmie standardow¹ lub wybran¹
            if isdir(temp_loc):
                self.location = self.entry_location.get()
            else:
                self.print_error_message(message="* Podano bledna lokalizacje!")
                correct_location = False

        if url:  # czy url jest poprawny
            if match('https://open\.spotify\.com/track/[^/]+', url) or \
                    match('https://open\.spotify\.com/playlist/[^/]+', url) or \
                    match('https://open\.spotify\.com/album/[^/]+', url):
                if '?' in url:
                    url = url.split('?')[0]
                correct_url = True
            else:
                self.print_error_message(message="* Podano bledny adres url!")
        else:  # url jest pusty
            self.print_error_message(message="* Nie podano adresu url!")

        # self.print_error_message(message=f"loc: {str(correct_location)}, url: {str(correct_url)}\n"
        #                                  f"loc: {self.location}, url: {url}")

        if correct_url and correct_location:  # wszystko ok
            # self.print_error_message(message="* ALL GOOD")
            self.main(self.location, url)


    def print_error_message(self, message):
        self.textbox_status.delete('1.0', 'end')
        self.textbox_status.configure(text_color='red')
        self.textbox_status.insert("0.0", message)

    def print_status(self, message):  # ?????
        self.textbox_status.delete('1.0', 'end')
        self.textbox_status.configure(text_color='green')
        self.textbox_status.insert("0.0", '<<<-   PODSUMOWANIE   ->>>\n\n')
        self.textbox_status.configure(text_color='white')
        self.textbox_status.insert('end', message)

    def change_placeholder_text(self):
        temp_loc = self.ask_for_directory()

        if temp_loc:
            self.location = temp_loc
            self.entry_location.destroy()
            self.entry_location = ctk.CTkEntry(self,
                                               placeholder_text=self.location,
                                               placeholder_text_color='black',
                                               text_color='black',
                                               fg_color='#9c9c9c',
                                               border_color='#575757',
                                               border_width=2,
                                               corner_radius=20)
            self.entry_location.grid(row=0, column=0, columnspan=2, padx=(20, 0), pady=(33, 20), sticky="new")

    # pobiera systemow¹ lokalizacjê folderu Muzyka w Windows
    def get_music_folder_path(self):
        current_user = getuser()
        music_folder_path = f'C:/Users/{current_user}/Music/Spotify'

        return music_folder_path
