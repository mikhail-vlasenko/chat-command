import os.path
import pickle

from basic_chat import ChatCommand

chat = ChatCommand('', '')

if not os.path.exists(chat.history_file_path):
    print("No chat history found.")
    exit()

with open(chat.history_file_path, 'rb') as file:
    messages = pickle.load(file)
    for message in messages:
        print(message['role'] + ':')
        print(message['content'])
        print()
