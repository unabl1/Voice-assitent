import sys
import pyttsx3
import os
import json
import webbrowser
import random
import traceback
import googletrans
import datetime
import requests
import sqlite3
import speech_recognition as sr
from OwnerPerson import OwnerPerson
from VoiceAssistant import VoiceAssistant
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit, QTableWidget, \
    QTableWidgetItem, QTextEdit, QFileDialog, QHBoxLayout
import pathes
from translate import Translator



class SmartAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Умный Ассистент")
        self.setGeometry(300, 300, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        input_layout = QHBoxLayout()
        output_layout = QVBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Введите команду...")
        input_layout.addWidget(self.input_text)
        send_button = QPushButton("Отправить")
        send_button.clicked.connect(self.process_command)
        input_layout.addWidget(send_button)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)

        open_window_button = QPushButton("todo list")
        open_window_button.clicked.connect(self.open_second_window)
        input_layout.addWidget(open_window_button)
        
        record_voice_button = QPushButton("Ввод с помощью голоса")
        record_voice_button.clicked.connect(self.record_voice)
        output_layout.addWidget(record_voice_button)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def record_voice(self):
        with self.microphone as source:
            print("Слушаю...")
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language=OwnerPerson.native_language)
                words_command = text.split(' ')
                for phrase, function in commands.items():
                    for word in words_command:
                        if word.lower() in phrase:
                            return function(text)
                play_topic_withdrawal()
                return f"Нет искомой функции"
            except sr.UnknownValueError:
                incomprehensible_speech()
            except sr.RequestError as e:
                print(f"Ошибка при запросе к сервису распознавания: {e}")

    def open_second_window(self):
        self.app_window = ScheduleApp()
        self.setCentralWidget(self.app_window)
        self.setWindowTitle('Smart Assistant App')

    def process_command(self):
        command = self.input_text.toPlainText()
        response = self.process_command_logic(command)
        self.output_text.append(response)
        self.input_text.clear()

    def process_command_logic(self, command, *args):
        words_command = command.split(' ')
        for phrase, function in commands.items():
            for word in words_command:
                if word.lower() in phrase:
                    return function(command)
        play_topic_withdrawal()
        return f"Нет искомой функции"


class ScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Schedule App")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.label = QLabel("Schedule App")
        self.layout.addWidget(self.label)

        self.name_label = QLabel("Event Name:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.date_label = QLabel("Event Date:")
        self.date_input = QLineEdit()
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_input)

        self.description_label = QLabel("Event Description:")
        self.description_input = QTextEdit()
        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.description_input)

        self.add_button = QPushButton("Add Event")
        self.add_button.clicked.connect(self.add_event)
        self.layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Event")
        self.edit_button.clicked.connect(self.edit_event)
        self.layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Event")
        self.delete_button.clicked.connect(self.delete_event)
        self.layout.addWidget(self.delete_button)

        self.read_tasks_button = QPushButton("Read Tasks")
        self.read_tasks_button.clicked.connect(self.read_tasks)
        self.layout.addWidget(self.read_tasks_button)

        self.return_back_button = QPushButton("Return Back")
        self.return_back_button.clicked.connect(self.return_back)
        self.layout.addWidget(self.return_back_button)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Event Name", "Description", "Event Date"])
        self.layout.addWidget(self.table)

        self.central_widget.setLayout(self.layout)

        self.create_tables()

    def create_tables(self):
        connection_schedule = sqlite3.connect("schedule.db")
        cursor_schedule = connection_schedule.cursor()

        cursor_schedule.execute('''CREATE TABLE IF NOT EXISTS events
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              name TEXT,
                              date TEXT,
                              description TEXT)''')

        connection_schedule.commit()
        connection_schedule.close()

        connection_users = sqlite3.connect("users.db")
        cursor_users = connection_users.cursor()

        cursor_users.execute('''CREATE TABLE IF NOT EXISTS users
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              username TEXT,
                              email TEXT,
                              background_image BLOB)''')

        connection_users.commit()
        connection_users.close()

        self.load_data()

    def load_data(self):
        connection = sqlite3.connect("schedule.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()

        self.table.setRowCount(len(events))

        for row, event in enumerate(events):
            for col, value in enumerate(event[1:]):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)

        connection.close()

    def add_event(self):
        name = self.name_input.text()
        date = self.date_input.text()
        description = self.description_input.toPlainText()

        if name and date:
            connection = sqlite3.connect("schedule.db")
            cursor = connection.cursor()

            cursor.execute("INSERT INTO events (name, date, description) VALUES (?, ?, ?)", (name, date, description))

            connection.commit()
            connection.close()

            self.name_input.clear()
            self.date_input.clear()
            self.description_input.clear()

            self.load_data()

    def edit_event(self):
        selected_row = self.table.currentRow()

        if selected_row >= 0:
            id = self.table.item(selected_row, 0).text()
            name = self.name_input.text()
            date = self.date_input.text()
            description = self.description_input.toPlainText()

            if name and date:
                connection = sqlite3.connect("schedule.db")
                cursor = connection.cursor()

                cursor.execute("UPDATE events SET name=?, date=?, description=? WHERE id=?", (name, date, description, id))

                connection.commit()
                connection.close()

                self.name_input.clear()
                self.date_input.clear()
                self.description_input.clear()

                self.load_data()

    def delete_event(self):
        selected_row = self.table.currentRow()

        if selected_row >= 0:
            id = self.table.item(selected_row, 0).text()

            connection = sqlite3.connect("schedule.db")
            cursor = connection.cursor()

            cursor.execute("DELETE FROM events WHERE id=?", (id,))

            connection.commit()
            connection.close()

            self.load_data()

    def read_tasks(self):
        connection = sqlite3.connect("schedule.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM events")
        tasks = cursor.fetchall()

        connection.close()

        for task in tasks:
            play_voice_assistant_speech(translator.get("Event Name {}").format(task[1]))
            play_voice_assistant_speech(translator.get("Event Date {}").format(task[2]))
            play_voice_assistant_speech(translator.get("Description {}").format(task[3]))

    def return_back(self):
        self.window = SmartAssistantApp()
        self.setCentralWidget(self.window)
        self.setWindowTitle('Smart Assistant App')


class Translation:
    with open("translations.json", "r", encoding="UTF-8") as file:
        translations = json.load(file)

    def get(self, text: str):
        if text in self.translations:
            return self.translations[text][assistant.speech_language]
        return text


def translate_text(input_text, target_language='ru'):
    translator= Translator(to_lang=target_language)
    translation = translator.translate(input_text)
    return translation

def play_voice_assistant_speech(text_to_speech):
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()  


def play_greetings(*args: tuple):
    greetings = [
        translator.get("Hello, {}! How can I help you today?").format(person.name),
        translator.get("Good day to you {}! How can I help you today?").format(person.name)
    ]
    play_voice_assistant_speech(greetings[random.randint(0, len(greetings) - 1)])
    return translator.get("Hello, {}! How can I help you today?").format(person.name)


def play_farewell_and_quit(*args: tuple):
    farewells = [
        translator.get("Goodbye, {}! Have a nice day!").format(person.name),
        translator.get("See you soon, {}!").format(person.name)
    ]
    play_voice_assistant_speech(farewells[random.randint(0, len(farewells) - 1)])
    ttsEngine.stop()
    quit()


def play_topic_withdrawal(*args: tuple):
    withdrawal = [
        translator.get("I'm here to help you {}").format(person.name),
        translator.get("{}, the request is not clear, use the 'help' command").format(person.name)
    ]
    play_voice_assistant_speech(withdrawal[random.randint(0, len(withdrawal) - 1)])


def incomprehensible_speech(*args: tuple):
    play_voice_assistant_speech(translator.get("Speech not recognized"))


def search_for_term_on_google(*args: tuple):
    if not args[0]: return
    search_term = "".join(args[0])
    search_term_splited = str(search_term.split(" ")[1:])
    url = "https://google.com/search?q=" + search_term[5:]
    webbrowser.get().open(url)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on google").format(search_term_splited))
    return translator.get("Here is what I found for {} on google").format(search_term_splited)


def search_for_video_on_youtube(*args: tuple):
    if not args[0]: return
    search_term = "".join(args[0])
    search_term_splited = str(search_term.split(" ")[1:])
    url = "https://www.youtube.com/results?search_query=" + search_term_splited
    webbrowser.get().open(url)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on youtube").format(search_term_splited))
    return translator.get("Here is what I found for {} on youtube").format(search_term_splited)


def get_translation(*args: tuple):
    if not args[0]: return
    search_term = "".join(args[0])
    search_term_splited = str(search_term.split(" ")[1:])
    google_translator = googletrans.Translator()
    translation_result = ""
    old_assistant_language = assistant.speech_language
    try:
        if assistant.speech_language != person.native_language:
            translation_result = google_translator.translate(search_term_splited, 
                                                      src=person.target_language,
                                                      dest=person.native_language)

            play_voice_assistant_speech("The translation for {} in Russian is".format(search_term_splited))

            assistant.speech_language = person.native_language
            setup_assistant_voice()

            return "The translation for {} in Russian is".format(search_term_splited)
        else:
            translation_result = google_translator.translate(search_term_splited,
                                                      src=person.native_language,
                                                      dest=person.target_language)
            play_voice_assistant_speech("По-английски {} будет как".format(search_term_splited))
            assistant.speech_language = person.target_language
            setup_assistant_voice()
        play_voice_assistant_speech(translation_result.text)
        return "По-английски {} будет как".format(search_term_splited)
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()

    finally:
        assistant.speech_language = old_assistant_language
        setup_assistant_voice()


def get_weather(*args: tuple):
    if not args[0]: return

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        'q': OwnerPerson.home_city,
        'appid': pathes.api_key,
        'units': 'metric'  # Можно изменить на 'imperial' для температуры в Фаренгейтах
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
    

            play_voice_assistant_speech(translator.get("Current weather in {}").format(translate_text(OwnerPerson.home_city)))
            play_voice_assistant_speech(translator.get("Temperature: {}° Celsius").format((temperature)))
            play_voice_assistant_speech(translator.get("Description: {}").format(translate_text(description)))
        
            return translator.get("Temperature: {}° Celsius").format((temperature))
        else:
            play_voice_assistant_speech(traceback.get("mistake"))
            return(f"Ошибка {response.status_code}: {data['message']}")
    
    except Exception as e:
        return(f"Произошла ошибка: {e}")


def change_language(*args: tuple):
    assistant.speech_language = "ru" if assistant.speech_language == "en" else "en"
    setup_assistant_voice()
    return("Language switched to " + assistant.speech_language, "cyan")


def run_person_through_social_nets_databases(*args: tuple):
    if not args[0]: return
    google_search_term = "".join(args[1:])
    vk_search_term = "".join(args[1:])
    fb_search_term = "".join(args[1:])
    url = "https://google.com/search?q=" + google_search_term + " site: vk.com"
    webbrowser.get().open(url)
    url = "https://google.com/search?q=" + google_search_term + " site: facebook.com"
    webbrowser.get().open(url)
    vk_url = "https://vk.com/people/" + vk_search_term
    webbrowser.get().open(vk_url)
    fb_url = "https://www.facebook.com/public/" + fb_search_term
    webbrowser.get().open(fb_url)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on social nets").format(google_search_term))
    return translator.get("Here is what I found for {} on social nets").format(google_search_term)


def get_time(*args: tuple):
    strTime = datetime.datetime.now().strftime("%H:%M:%S")
    play_voice_assistant_speech(translator.get("At the moment {}").format(strTime))
    return translator.get("At the moment {}").format(strTime)


def play_music(*args: tuple):
    play_voice_assistant_speech(translator.get("The moment I open the music folder"))
    os.startfile(pathes.pathMusic)
    return translator.get("The moment I open the music folder")


def open_PyCharm(*args: tuple):
    play_voice_assistant_speech(translator.get("Now I will open a paycharm"))
    os.startfile(pathes.pathPaycharm)
    return translator.get("Now I will open a paycharm")


def help_peron(*args: tuple):
    play_voice_assistant_speech(translator.get("Here's a list of my commands and code words for you"))
    return help_command

commands = {
    ("hello", "hi", "morning", "привет"): play_greetings,
    ("bye", "goodbye", "quit", "exit", "stop", "пока"): play_farewell_and_quit,
    ("search", "google", "find", "найди"): search_for_term_on_google,
    ("video", "youtube", "watch", "видео"): search_for_video_on_youtube,
    ("translate", "interpretation", "translation", "перевод", "перевести", "переведи"): get_translation,
    ("language", "язык"): change_language,
    ("weather", "forecast", "погода", "прогноз"): get_weather,
    ("time", "время"): get_time,
    ("help", "помощь"): help_peron,
    ("PyCharm", "пайчарм"): open_PyCharm,
    ("music", "музыка"): play_music,
    ("person", "человек"): run_person_through_social_nets_databases,
}


help_command = '''
    "hello", "hi", "morning", "привет": Приветствие,\n
    "bye", "goodbye", "quit", "exit", "stop", "пока": Прощание,\n
    "search", "google", "find", "найди": Поиск в интернете,\n
    "video", "youtube", "watch", "видео": Поиск видео,\n
    "translate", "interpretation", "translation", "перевод", "перевести", "переведи": Перевод,\n
    "language", "язык": поменять язык,\n
    "weather", "forecast", "погода", "прогноз": Погода,\n
    "time", "время": Точное время,\n
    "help", "помощь": Помощь,\n
    "PyCharm", "пайчарм": Открыть среду разработки,\n
    "music", "музыка": Включить музыку,\n
    "person", "человек": Найти человека\n
'''


def setup_assistant_voice():
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        ttsEngine.setProperty("voice", voices[0].id)      


if __name__ == "__main__":
    ttsEngine = pyttsx3.init()

    person = OwnerPerson()
    person.name = OwnerPerson.name
    person.home_city = OwnerPerson.home_city
    person.native_language = OwnerPerson.native_language
    person.target_language = OwnerPerson.target_language

    assistant = VoiceAssistant()
    assistant.name = VoiceAssistant.name
    assistant.sex = VoiceAssistant.sex
    assistant.speech_language = VoiceAssistant.speech_language

    setup_assistant_voice()
    translator = Translation()


    app = QApplication(sys.argv)
    window = SmartAssistantApp()
    window.show()
    sys.exit(app.exec_())