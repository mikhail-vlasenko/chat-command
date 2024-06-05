import sys
import os
import requests
import argparse
import logging
import pickle

import examples
from config import Config

logging.basicConfig(
    filename=f'{os.getenv("CHAT_COMMAND_PATH")}/basic.log',
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


SYSTEM_PROMPT = f"""
You are a helpful expert that assists the user with shell commands.
Your response should contain only the commands. No explanations or additional information.
All commands that need to be executed together should be on the same line.
Do not start your responses with the cd command into the current directory.
The commands should be complete and executable as they are. So do not use placeholders like <your_file>.

If, given the context, multiple responses are equally likely, output up to 3 possible variants, separated by the new line characters.
In case you believe more context is needed, produce a command that, when executed, would provide this context as its output. Append \"# for context\" at the end of such command.
{examples.context_request()}

If you provide multiple suggestions in one response, make sure they are significantly different from each other, and none of them repeats the command that you need to fix.
It is unlikely the user wants 3 different ways to obtain more context: mix in a potential solution as well.
"""


class ChatCommand:
    def __init__(self, last_command, last_output):
        self.config = Config()

        self.last_chat_command = os.getenv("CHAT_COMMAND_LAST_COMMAND", "")
        self.last_chat_output = self.truncate_output(os.getenv("CHAT_COMMAND_LAST_OUTPUT", ""))
        self.last_command = last_command
        self.last_output = self.truncate_output(last_output)
        # if the last command was the one executed by `chat` (and was not reran),
        # we dont need to mention it after our request, as it will be in the chat history already
        self.dont_mention_last_command = self.last_chat_command == self.last_command and self.last_output == ""

        self.system_prompt = SYSTEM_PROMPT
        self.messages = self.init_chat_history()

    def get_api_response(self, data):
        request_data = {
            "model": self.config.model,
            "max_tokens": 200,
            "temperature": 0.,
        }
        request_data.update(data)
        logging.info(f"Asking {request_data['model']} for suggestions.")
        logging.info(f"Sending request with prompt:\n{request_data['messages'][-1]['content']}")
        response = requests.post(self.config.api_url, json=request_data, headers=self.config.headers)
        logging.info(f"Received response: {response.json()}")
        if response.status_code != 200:
            print(f"❌ LLM request failed:\n {response.json()}")
            sys.exit(1)
        return response.json()

    def make_prompt_fix_command(self, clipboard=False):
        print("🤖 Attempting to fix the last command...")
        prompt = self.init_prompt(include_last_command=True)
        if self.dont_mention_last_command:
            prompt += f"Something still went wrong."
        else:
            prompt += f"Please fix this shell command:"
            prompt += f"\n{self.last_command}"
            prompt += f"\nThis command's current output:\n{self.last_output}\nend of output."
        # prompt += f"\nThe current directory is: {os.getcwd()}"
        prompt += self.add_clipboard_content(clipboard)
        prompt += "\nSuggest a command to fix the issue."
        return prompt

    def make_prompt_suggest_from_text(self, text, clipboard=False):
        print("🤖 Generating suggestions based on the provided query...")
        prompt = self.init_prompt(include_last_command=True)
        prompt += f"I want to do the following: {text}"
        if not self.dont_mention_last_command:
            prompt += f"\nHere is the last executed command (it may not be helpful to this request): {self.last_command}"
            prompt += f"\nOutput of the last command (may also not be helpful):\n{self.last_output}\nend of output."
        # prompt += f"\nThe current directory is: {os.getcwd()}"
        prompt += self.add_clipboard_content(clipboard)

        prompt += "\nIf the provided information is enough, suggest a command to achieve the goal."
        prompt += "\nOtherwise, suggest a command that can provide the necessary context."
        return prompt

    def make_prompt_additional_instructions(self, text):
        print("🤖 Considering the additional instructions...")
        # do not include the last command, as nothing was executed since the last llm request
        prompt = self.init_prompt(include_last_command=False)
        prompt += f"I do not want to execute any of these commands. Here are some additional instructions:"
        prompt += f"\n{text}"
        prompt += f"\nConsidering this, suggest up to 3 commands that would be helpful."
        return prompt

    def make_prompt_received_context(self):
        print("🤖 Analyzing the context...")
        prompt = self.init_prompt(include_last_command=True)
        prompt += f"Given this new context, continue solving the task."
        return prompt

    def produce_llm_command(self, request_type, **kwargs):
        """
        Presents command choices to the user based on the given request type.
        Recurses when the user provides additional instructions.
        :param request_type:
        :param kwargs:
        :return:
        """
        if request_type == "fix_command":
            prompt = self.make_prompt_fix_command(**kwargs)
        elif request_type == "suggest_from_text":
            prompt = self.make_prompt_suggest_from_text(**kwargs)
        elif request_type == "additional_instructions":
            prompt = self.make_prompt_additional_instructions(**kwargs)
        elif request_type == "received_context":
            prompt = self.make_prompt_received_context()
        else:
            raise ValueError(f"Unknown request type: {request_type}")

        self.append_user_message(prompt)
        data = {"messages": self.messages}
        suggestions = self.extract_suggestions(self.get_api_response(data))
        # request selection until the user inputs something other than a new instruction
        self.choose_command(suggestions)

    def choose_command(self, suggestions):
        """
        Prompts the user to choose a command from the suggestions.
        Distinguishes between a single suggestion and multiple suggestions.
        In case the user's response is not one of the given options,
        it is treated as addressed to the LLM, and thus it is sent to the model.
        :param suggestions: list of 1 or more suggestions
        :return:
        """
        self.messages.append({
            "role": "assistant",
            "content": "\n".join(suggestions)
        })

        try:
            if len(suggestions) > 1:
                print("ℹ️ Suggested commands:")
                for index, suggestion in enumerate(suggestions, start=1):
                    print(f"{index}. {suggestion}")

                print(f"❔ Enter your selection ([1]-{len(suggestions)}/n/<new instructions>): ", end="")
                response = input()
                if response.lower() == 'n':
                    self.append_user_message("I do not want to execute any of these commands.")
                    self.write_history()
                else:
                    try:
                        if response == '':
                            response = '1'
                        response = int(response) - 1
                        if response < 0 or response >= len(suggestions):
                            raise ValueError
                        self.send_command(suggestions[response])
                    except ValueError:
                        self.produce_llm_command("additional_instructions", text=response)
            else:
                suggestion = suggestions[0]
                print(f"ℹ️ Suggested command: {suggestion}")
                response = input("❔ Execute? ([y]/n/<new instructions>): ")
                if response.lower() == 'y' or response == '':
                    self.send_command(suggestion)
                elif response.lower() == 'n':
                    self.append_user_message("I do not want to execute any of these commands.")
                    self.write_history()
                else:
                    self.produce_llm_command("additional_instructions", text=response)
        except KeyboardInterrupt:
            print()
            sys.exit(1)

    def send_command(self, command):
        context_flag = False
        if "# for context" in command:
            context_flag = True

        # cut off the comment
        command = command.split("#")[0].strip()

        with open(self.config.result_file_path, 'w') as file:
            file.write(f"{command}\n{self.config.conv_id}\n{int(context_flag)}\n")
        logging.info(f"Command written to file: {command}")
        self.write_history()

    def init_chat_history(self):
        """
        Creates the chat history to be sent to the model.
        Includes the system prompt and previous interactions in this session.
        :return:
        """
        chat_history = [{"role": "system", "content": self.system_prompt}]
        if os.environ.get("CHAT_COMMAND_CONV_ID"):
            with open(self.config.history_file_path, 'rb') as file:
                chat_history.extend(pickle.load(file))
            logging.info(f"Chat history loaded from file: {self.config.history_file_path}")
        return chat_history

    def init_prompt(self, include_last_command=True):
        """
        Initializes the user prompt for the model.
        Considers the last message in history, as well as the last command and its output.
        :param include_last_command:
        :return: prompt that is empty or has the new line at the end
        """
        prompt = ""
        if self.messages[-1]["role"] == "user":
            # this ensures we don't write 2 user messages in a row or overwrite some information
            prompt = self.messages[-1]["content"] + "\n"
            self.messages.pop()
        if include_last_command and self.last_chat_command:
            prompt += f"I executed {self.last_chat_command}"
            prompt += f"\nThe output was:\n{self.last_chat_output}\nend of output.\n"
        return prompt

    def append_user_message(self, user_message):
        self.messages.append({"role": "user", "content": user_message})

    def write_history(self):
        # system prompt is not written, as it is assumed to be always the same
        with open(self.config.history_file_path, 'wb') as file:
            pickle.dump(self.messages[1:], file)

    def extract_suggestions(self, response):
        """
        Extracts the suggestions from the model's response json.
        :param response: json
        :return: list of suggestions
        """
        suggestions = self.clean_suggestions(response['choices'][0]['message']['content'].splitlines())
        logging.info(f"Extracted clean suggestions: {suggestions}")
        return suggestions

    def clean_suggestions(self, suggestions):
        """
        Performs some cleaning as LLM's output may be in wrong format.
        :param suggestions:
        :return:
        """
        cleaned_suggestions = []
        # merge lines if model outputted # for context on a new line
        for i in range(1, len(suggestions)):
            if suggestions[i].startswith("# for context"):
                suggestions[i-1] += " " + suggestions[i]
                suggestions[i] = ""

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

    @staticmethod
    def add_clipboard_content(clipboard):
        if clipboard:
            import pyperclip

            print("📋 Reading clipboard content.")
            clipboard_content = pyperclip.paste()
            return f"\nClipboard content that might be helpful:\n{clipboard_content}\nend of clipboard content."
        return ""

    @staticmethod
    def truncate_output(output):
        max_length = 1000
        if len(output) > max_length:
            return output[:max_length//2] + "\n...\n" + output[-(max_length//2):]
        return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("output")
    parser.add_argument("query", help="Description of what needs to be done (or empty for nothing)")
    parser.add_argument("clipboard", type=int, choices=[0, 1],
                        help="Include clipboard content in the prompt for suggestions (0 or 1)")
    parser.add_argument("with_context", type=int, choices=[0, 1],
                        help="This is a follow-up request that provides context")

    args = parser.parse_args()
    # unpack the values
    args.clipboard = bool(args.clipboard)
    args.with_context = bool(args.with_context)
    if args.query == "\"\"":
        args.query = ""

    chat = ChatCommand(args.command, args.output)
    if args.with_context:
        chat.produce_llm_command("received_context")
    elif args.query:
        chat.produce_llm_command("suggest_from_text", text=args.query, clipboard=args.clipboard)
    else:
        chat.produce_llm_command("fix_command", clipboard=args.clipboard)


if __name__ == "__main__":
    main()
