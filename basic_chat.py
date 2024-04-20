import sys
import os
import requests
import argparse
import pyperclip
import logging


logging.basicConfig(filename='chat_command.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


system_prompt = """
You are a helpful system that assists a user with shell commands.
Start your response should contain only the commands. No explanations or additional information.
All commands that need to be executed together should be on the same line.
"""


def send_to_openai(command, output, api_key, clipboard_content=None):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"Shell command troubleshooting: \nCommand: {command}\n"
    prompt += f"Output:\n{output}\nend of output."

    prompt += f"\nThe current directory is: {os.getcwd()}"

    if clipboard_content:
        prompt += f"\nClipboard content that might be helpful:\n{clipboard_content}\nend of clipboard content."
    prompt += "\nSuggest a command to fix the issue."
    prompt += ("\nIf, given the context, there are multiple possible fixes, "
               "output up to 3 fixes, separated by the new line characters.")
    prompt += "\nDo not start the fixes with the cd command into the current directory."

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 200,
        "temperature": 0.,
    }
    logging.info(f"Sending request with prompt: {data['messages'][1]['content']}")
    response = requests.post(url, json=data, headers=headers)
    logging.info(f"Received response: {response.json()}")
    try:
        suggestions = response.json()['choices'][0]['message']['content'].splitlines()
        logging.info(f"Extracted suggestions: {suggestions}")
        return suggestions
    except KeyError:
        logging.error("Failed to parse response from OpenAI.")
        return "Error: Failed to obtain valid response from OpenAI."


def choose_command(suggestions):
    if len(suggestions) > 1:
        print("Select the fix:")
        for index, suggestion in enumerate(suggestions, start=1):
            print(f"{index}. {suggestion}")

        try:
            choice = int(input("Enter the number of the command to execute: ")) - 1
        except KeyboardInterrupt:
            sys.exit(1)

        if 0 <= choice < len(suggestions):
            send_command(suggestions[choice])
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
    else:
        suggestion = suggestions[0]
        print(f"Suggested fix: {suggestion}")
        execute = input("Execute? ([y]/n) ").lower()
        if execute != 'n':
            send_command(suggestion)
        else:
            print("Aborting.")


def send_command(command):
    file_path = os.path.expanduser('~/chat_command/command_to_execute.txt')

    with open(file_path, 'w') as file:
        file.write(command + '\n')

    logging.info(f"Command written to file: {command}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clipboard", action="store_true", help="Include clipboard content in the prompt for suggestions")
    parser.add_argument("command")
    parser.add_argument("output")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    clipboard_content = pyperclip.paste() if args.clipboard else None
    suggestions = send_to_openai(args.command, args.output, api_key, clipboard_content)
    if isinstance(suggestions, list):
        choose_command(suggestions)


if __name__ == "__main__":
    main()
