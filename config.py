import os
import sys
import time


BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'


class Config:
    def __init__(self):
        if os.getenv("CHAT_COMMAND_API_KEY"):
            self.api_key = os.getenv("CHAT_COMMAND_API_KEY")
        else:
            self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("❌ OpenAI API key not found. "
                  "Please set the OPENAI_API_KEY or CHAT_COMMAND_API_KEY environment variable.")
            sys.exit(1)

        self.path = os.getenv("CHAT_COMMAND_PATH")
        if not self.path:
            print("❌ CHAT_COMMAND_PATH environment variable is not set. "
                  "It probably should be \"~/.chat_command.\"")
            sys.exit(1)

        self.api_url = os.getenv("CHAT_COMMAND_API_URL", "https://api.openai.com/v1/chat/completions")
        self.model = os.getenv("CHAT_COMMAND_MODEL", "gpt-3.5-turbo")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.result_file_path = os.path.join(self.path, 'command_to_execute.txt')
        self.conv_id = os.getenv("CHAT_COMMAND_CONV_ID")
        if not self.conv_id:
            # also updates the value if its empty string
            self.conv_id = time.time()
        self.conv_id = int(self.conv_id)
        self.history_file_path = os.path.join(self.path, "chat_history", f"{self.conv_id}.pkl")

    @staticmethod
    def configuration_help_string():
        return (
            f"⚙️ {BOLD}{UNDERLINE}Configuration Help:{RESET}\n\n"
            f"You can set the following environment variables in your shell configuration file (e.i. ~/.bashrc) "
            f"to be used by the chat command.\n"
            f"{BOLD}Environment Variables:{RESET}\n"
            f"  - {BOLD}CHAT_COMMAND_API_KEY{RESET}: The API key for accessing the chat command service. If not set, "
            f"the {BOLD}OPENAI_API_KEY{RESET} is used as a fallback.\n"
            f"  - {BOLD}OPENAI_API_KEY{RESET}: Alternative API key if {BOLD}CHAT_COMMAND_API_KEY{RESET} is not set.\n"
            f"  - {BOLD}CHAT_COMMAND_API_URL{RESET}: The URL for the chat command API. Defaults to "
            f"\"https://api.openai.com/v1/chat/completions\"\n"
            f"  - {BOLD}CHAT_COMMAND_MODEL{RESET}: The model used for completion. Defaults to \"gpt-3.5-turbo\"\n"
            f"  - {BOLD}CHAT_COMMAND_PATH{RESET}: The file path for storing chat command data. "
            f"By default, is set to \"~/.chat_command\" during installation.\n"
        )
