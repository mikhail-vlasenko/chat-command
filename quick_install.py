import pyperclip
import os


# todo: extend install_chat_command.sh to ask for key and optially write it to .bashrc
INSTALL_STRING = f"""sudo apt update
sudo apt install git-all
git clone https://github.com/mikhail-vlasenko/chat-command.git
cd chat-command
sudo apt install python3-pip
pip3 install -r requirements.txt
export CHAT_COMMAND_PATH="$HOME/.chat_command"
source install_chat_command.sh
echo "export CHAT_COMMAND_PATH="$CHAT_COMMAND_PATH >> ~/.bashrc
echo "export CHAT_COMMAND_PYTHON="$(which python3) >> ~/.bashrc
echo "source "$CHAT_COMMAND_PATH"/chat_wrapper.sh" >> ~/.bashrc
echo "export OPENAI_API_KEY="{os.getenv('OPENAI_API_KEY')} >> ~/.bashrc
source ~/.bashrc
echo -e "\nInstallation complete. You can now use the chat command. \\U1F916"
"""

if __name__ == "__main__":
    pyperclip.copy(INSTALL_STRING)
    print("Installation string is copied to clipboard.")
