import telebot
import requests
import speech_recognition as speech
import moviepy.editor as movie
from pydub import AudioSegment
import os

#AUDIO AND VIDEO LOCATION
AUDIO_PATH = os.path.join(os.getcwd(), 'audio')
VIDEO_PATH = os.path.join(os.getcwd(), 'video')
#Token for bot 
BOT_TOKEN = "5859632408:AAELnKd79ttkvVPMRkVxImwm8ipL1yR0lLU" #Change this with your own BOT_TOKEN if you want
                                                            # Test on your own bot
 
bot = telebot.TeleBot(BOT_TOKEN)
recognizer = speech.Recognizer()

#Default Language is english
language_choice = "en_US"



@bot.message_handler(commands=["start", "help"])
def start(message):
    text = (
          f'Nice to meet you! I am ConvertToText bot\n'
          f'My job is to convert those pesky video/voice'
          f' messages into easy-to-read text\n'
          f'To get started just send the file you want'
          f' to convert to text\nCurrently I only support'
          f' English and Russian\n To choose language please'
          f' write /language english or /language russian\n'
          f'Do note that the default language is english'
          )
    bot.reply_to(message, text)

@bot.message_handler(commands=["language"])
def choose_language(message):
    text = message.text[10:]
    text = text.upper()
    global language_choice
    if (text == "ENGLISH"):
        language_choice = "en_US"
    elif (text=="RUSSIAN"):
        language_choice = "ru_RU"
    bot.reply_to(message,f'Language changed to {message.text[10:]}')


@bot.message_handler(content_types=['voice'])
def audio_handling(message):
    file_info = bot.get_file(message.voice.file_id)
    file_name = file_info.file_path.split('/')[1]
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(BOT_TOKEN, file_info.file_path))
    audio = audio_converter(file_name, file)
    response = text_recognition(audio)
    empty_folders()
    bot.reply_to(message, response)

@bot.message_handler(content_types=['video_note'])
def video_handling(message):
    file_info = bot.get_file(message.video_note.file_id)
    file_name = file_info.file_path.split('/')[1]
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(BOT_TOKEN, file_info.file_path))
    audio = video_converter(file_name, file)
    response = text_recognition(audio)
    empty_folders()
    bot.reply_to(message, response)

def audio_converter(file_name, file):
    if not os.path.exists(AUDIO_PATH):
        os.makedirs(AUDIO_PATH)
    path_ogg = os.path.join(AUDIO_PATH, f"{file_name}.ogg")
    path_wav = os.path.join(AUDIO_PATH, f"{file_name}.wav")
    with open(path_ogg, 'wb') as f:
        f.write(file.content)
    sound = AudioSegment.from_ogg(path_ogg)
    sound.export(path_wav, format="wav")
    return path_wav

def video_converter(file_name, file):
    if not os.path.exists(VIDEO_PATH):
        os.makedirs(VIDEO_PATH)
    if not os.path.exists(AUDIO_PATH):
        os.makedirs(AUDIO_PATH)
    path_mp4 = os.path.join(VIDEO_PATH, f"{file_name}.mp4")
    path_wav = os.path.join(AUDIO_PATH, f"{file_name}.wav")
    with open(path_mp4, 'wb') as f:
        f.write(file.content)
    clip = movie.VideoFileClip(path_mp4)
    clip.audio.write_audiofile(path_wav)
    return path_wav

def empty_folders():
    folders_to_clear = []
    if os.path.isdir(VIDEO_PATH):
        folders_to_clear.append(VIDEO_PATH)
    if os.path.isdir(AUDIO_PATH):
        folders_to_clear.append(AUDIO_PATH)

    for folder in folders_to_clear:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                pass
    

def text_recognition(audio):
    with speech.AudioFile(audio) as source:
        audio_data = recognizer.record(source)
        global language_choice
        print(language_choice)
        try:
            text= recognizer.recognize_google(audio_data,language=language_choice)
        except speech.UnknownValueError:
               text = "Sorry I couldn't understand anything :C "
        return text

while True:
    try:
        bot.polling(2)
    except Exception as error:
        print(error)


