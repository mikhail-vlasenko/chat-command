import sys
import os
import requests
import argparse
import logging
import time
import pickle

import examples


logging.basicConfig(
    filename=f'{os.getenv("CHAT_COMMAND_PATH")}/basic.log',
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


SYSTEM_PROMPT = """
You are a helpful expert that assists the user with shell commands.
Your response should contain only the commands. No explanations or additional information.
All commands that need to be executed together should be on the same line.
Do not start your responses with the cd command into the current directory.
The commands should be complete and executable as they are. So do not use placeholders like <your_file>.

If, given the context, multiple responses are equally likely, output up to 3 possible variants, separated by the new line characters.
In case you believe more context is needed, produce a command that, when executed, would provide this context as its output. Append \"# for context\" at the end of such command.
"""


class ChatCommand:
    def __init__(self, last_command, last_output):
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
        cond_id = os.getenv("CHAT_COMMAND_CONV_ID")
        if cond_id:
            self.conv_id = int(cond_id)
        else:
            self.conv_id = int(time.time())
        self.history_file_path = os.path.join(self.path, "chat_history", f"{self.conv_id}.pkl")

        self.last_chat_command = os.getenv("CHAT_COMMAND_LAST_COMMAND", "")
        self.last_chat_output = self.truncate_output(os.getenv("CHAT_COMMAND_LAST_OUTPUT", ""))
        self.last_command = last_command
        self.last_output = self.truncate_output(last_output)
        # if the last command was the one executed by `chat` (and was not reran),
        # we dont need to mention it after our request, as it will be in the chat history already
        self.dont_mention_last_command = self.last_chat_command == self.last_command and self.last_output == ""

        self.system_prompt = SYSTEM_PROMPT + "\n" + examples.context_request()
        self.messages = []

    def get_llm_response(self, data):
        request_data = {
            "model": "gpt-3.5-turbo",
            "max_tokens": 200,
            "temperature": 0.,
        }
        request_data.update(data)
        url = "https://api.openai.com/v1/chat/completions"
        logging.info(f"Asking {request_data['model']} for suggestions.")
        logging.info(f"Sending request with prompt:\n{request_data['messages'][-1]['content']}")
        response = requests.post(url, json=request_data, headers=self.headers)
        logging.info(f"Received response: {response.json()}")
        return response.json()

    def fix_command(self, clipboard=False):
        if self.dont_mention_last_command:
            prompt = f"Something still went wrong."
        else:
            prompt = f"Please fix this shell command:"
            prompt += f"\n{self.last_command}"
            prompt += f"\nThis command's current output:\n{self.last_output}\nend of output."

        # prompt += f"\nThe current directory is: {os.getcwd()}"
        prompt += self.add_clipboard_content(clipboard)
        prompt += "\nSuggest a command to fix the issue."

        self.messages = self.make_chat_history(prompt)
        data = {"messages": self.messages}

        suggestions = self.get_llm_response(data)['choices'][0]['message']['content'].splitlines()
        return suggestions

    def command_from_text(self, text, clipboard=False):
        prompt = f"I want to do the following: {text}"
        if not self.dont_mention_last_command:
            prompt += f"\nHere is the last executed command (it may not be helpful to this request): {self.last_command}"
            prompt += f"\nOutput of the last command (may also not be helpful):\n{self.last_output}\nend of output."
        # prompt += f"\nThe current directory is: {os.getcwd()}"
        prompt += self.add_clipboard_content(clipboard)

        prompt += "\nIf the provided information is enough, suggest a command to achieve the goal."
        prompt += "\nOtherwise, suggest a command that can provide the necessary context."

        self.messages = self.make_chat_history(prompt)
        data = {"messages": self.messages}

        suggestions = self.get_llm_response(data)['choices'][0]['message']['content'].splitlines()
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
                if (
                        suggestion.startswith("```") or
                        suggestion.startswith("#") or
                        suggestion.lower() == "or"
                ):
                    continue

                # sometimes the model "indexes" the suggestions
                if not suggestion.startswith("./"):
                    suggestion = suggestion.lstrip('0123456789. -')

                cleaned_suggestions.append(suggestion)
        return cleaned_suggestions

    def choose_command(self, suggestions):
        self.messages.append({
            "role": "assistant",
            "content": "\n".join(suggestions)
        })

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
        context_flag = False
        if "# for context" in command:
            context_flag = True

        # cut off the comment
        command = command.split("#")[0].strip()

        with open(self.result_file_path, 'w') as file:
            file.write(f"{command}\n{self.conv_id}\n{int(context_flag)}\n")

        self.write_history()

        logging.info(f"Command written to file: {command}")

    @staticmethod
    def add_clipboard_content(clipboard):
        if clipboard:
            import pyperclip

            print("Reading clipboard content.")
            clipboard_content = pyperclip.paste()
            return f"\nClipboard content that might be helpful:\n{clipboard_content}\nend of clipboard content."
        return ""

    def make_chat_history(self, user_message):
        """
        Creates the chat history to be sent to the model.
        :param user_message:
        :return:
        """
        chat_history = [{"role": "system", "content": self.system_prompt}]
        if os.environ.get("CHAT_COMMAND_CONV_ID"):
            with open(self.history_file_path, 'rb') as file:
                chat_history.extend(pickle.load(file))
            logging.info(f"Chat history loaded from file: {self.history_file_path}")

        full_message = ""
        if self.last_chat_command:
            full_message += f"I executed {self.last_chat_command}"
            full_message += f"\nThe output was:\n{self.last_chat_output}\nend of output."
        full_message += f"\n{user_message}"
        chat_history.append({"role": "user", "content": full_message})
        return chat_history

    def write_history(self):
        # system prompt is not written, as it is assumed to be always the same
        with open(self.history_file_path, 'wb') as file:
            pickle.dump(self.messages[1:], file)

    def truncate_output(self, output):
        max_length = 1000
        if len(output) > max_length:
            return output[:max_length//2] + "\n...\n" + output[-(max_length//2):]
        return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("output")
    parser.add_argument("query", nargs='?', default="", help="Description of what needs to be done (optional)")
    parser.add_argument("-c", "--clipboard", action="store_true",
                        help="Include clipboard content in the prompt for suggestions")

    args = parser.parse_args()

    chat = ChatCommand(args.command, args.output)
    if args.query:
        print("Generating suggestions based on the provided query.")
        suggestions = chat.command_from_text(args.query, args.clipboard)
    else:
        print("Attempting to fix the last command.")
        suggestions = chat.fix_command(args.clipboard)
    suggestions = chat.clean_suggestions(suggestions)
    logging.info(f"Extracted suggestions: {suggestions}")
    chat.choose_command(suggestions)


if __name__ == "__main__":
    main()
