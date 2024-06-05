import os.path
import pickle

from chat_command import ChatCommand


def make_bold(text):
    return f'\033[1m{text}\033[0m'


chat = ChatCommand('', '')

if not os.path.exists(chat.config.history_file_path):
    print("No chat history found.")
    exit()

with open(chat.config.history_file_path, 'rb') as file:
    messages = pickle.load(file)
    for message in messages:
        print(make_bold(message['role'] + ':'))
        print(message['content'])
        print()
