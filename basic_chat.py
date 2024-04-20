import sys
import os
import requests
import argparse
import pyperclip
import logging

import examples


logging.basicConfig(
    filename=f'{os.getenv("CHAT_COMMAND_PATH")}/basic.log',
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


system_prompt = """
You are a helpful system that assists a user with shell commands.
Start your response should contain only the commands. No explanations or additional information.
All commands that need to be executed together should be on the same line.
Do not start your responses with the cd command into the current directory.
The commands should be complete and executable as they are. So do not use placeholders like <your_file>.
If, given the context, multiple responses are equally likely, output up to 3 possible variants, separated by the new line characters.
"""


class ChatCommand:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            sys.exit(1)

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.path = os.getenv("CHAT_COMMAND_PATH")

        self.result_file_path = os.path.join(self.path, 'command_to_execute.txt')

    def get_llm_response(self, data):
        request_data = {
            "model": "gpt-3.5-turbo",
            "max_tokens": 200,
            "temperature": 0.,
        }
        request_data.update(data)
        url = "https://api.openai.com/v1/chat/completions"
        logging.info(f"Asking {request_data['model']} for suggestions.")
        logging.info(f"Sending request with prompt: {request_data['messages'][-1]['content']}")
        response = requests.post(url, json=request_data, headers=self.headers)
        logging.info(f"Received response: {response.json()}")
        return response.json()

    def fix_command(self, command, output, clipboard=False):
        prompt = f"Shell command troubleshooting: \nCommand: {command}\n"
        prompt += f"Output:\n{output}\nend of output."
        prompt += f"\nThe current directory is: {os.getcwd()}"
        prompt += self.add_clipboard_content(clipboard)

        prompt += "\nSuggest a command to fix the issue."
        prompt += "\nDo not start the fixes with the cd command into the current directory."

        data = {"messages": self.make_chat_history([
            {"role": "user", "content": prompt}
        ])}
        suggestions = self.get_llm_response(data)['choices'][0]['message']['content'].splitlines()
        logging.info(f"Extracted suggestions: {suggestions}")
        return suggestions

    def command_from_text(self, text, last_command, output, clipboard=False):
        prompt = f"I want to do the following: {text}"
        prompt += f"\nHere is the last executed command (it may not be helpful to this request): {last_command}"
        prompt += f"\nOutput of the last command (may also not be helpful):\n{output}\nend of output."
        prompt += f"\nThe current directory is: {os.getcwd()}"
        prompt += self.add_clipboard_content(clipboard)

        prompt += "\nIf the provided information is enough, suggest a command to achieve the goal."
        prompt += ("\nIn case you believe more context is needed, produce a command that, "
                   "when executed, would provide this context as its output. "
                   "Append \"#for context#\" in the beginning of such command.")

        prompt += examples.context_request()

        data = {"messages": self.make_chat_history([
            {"role": "user", "content": prompt}
        ])}
        suggestions = self.get_llm_response(data)['choices'][0]['message']['content'].splitlines()
        logging.info(f"Extracted suggestions: {suggestions}")
        return suggestions

    def clean_suggestions(self, suggestions):
        """
        Performs some cleaning as LLM's output may be in wrong format.
        :param suggestions:
        :return:
        """
        cleaned_suggestions = []
        for suggestion in suggestions:
            suggestion = suggestion.strip()
            if suggestion:
                if suggestion.startswith("```") or suggestion.lower() == "or":
                    continue
                cleaned_suggestions.append(suggestion)
        return cleaned_suggestions

    def choose_command(self, suggestions):
        if len(suggestions) > 1:
            print("Select a command to execute:")
            for index, suggestion in enumerate(suggestions, start=1):
                print(f"{index}. {suggestion}")

            try:
                choice = int(input("Enter the index of the command to execute: ")) - 1
            except KeyboardInterrupt:
                sys.exit(1)

            if 0 <= choice < len(suggestions):
                self.send_command(suggestions[choice])
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)
        else:
            suggestion = suggestions[0]
            print(f"Suggested command: {suggestion}")
            execute = input("Execute? ([y]/n) ").lower()
            if execute != 'n':
                self.send_command(suggestion)
            else:
                print("Aborting.")

    def send_command(self, command):
        if command.startswith("#for context#"):
            command = command[len("#for context#"):].strip()

        with open(self.result_file_path, 'w') as file:
            file.write(command + '\n')

        logging.info(f"Command written to file: {command}")

    @staticmethod
    def add_clipboard_content(clipboard):
        if clipboard:
            print("Reading clipboard content.")
            clipboard_content = pyperclip.paste()
            return f"\nClipboard content that might be helpful:\n{clipboard_content}\nend of clipboard content."
        return ""

    @staticmethod
    def make_chat_history(messages):
        chat_history = [{"role": "system", "content": system_prompt}]
        for message in messages:
            role = message['role']
            content = message['content']
            chat_history.append({"role": role, "content": content})
        return chat_history


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("output")
    parser.add_argument("query", nargs='?', default="", help="Description of what needs to be done (optional)")
    parser.add_argument("-c", "--clipboard", action="store_true",
                        help="Include clipboard content in the prompt for suggestions")

    args = parser.parse_args()

    chat = ChatCommand()
    if args.query:
        print("Generating suggestions based on the provided query.")
        suggestions = chat.command_from_text(args.query, args.command, args.output, args.clipboard)
    else:
        print("Attempting to fix the last command.")
        suggestions = chat.fix_command(args.command, args.output, args.clipboard)
    suggestions = chat.clean_suggestions(suggestions)
    chat.choose_command(suggestions)


if __name__ == "__main__":
    main()
