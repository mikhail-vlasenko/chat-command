import pyperclip
import os


INSTALL_STRING = f"""sudo apt update
sudo apt install git-all
git clone https://github.com/mikhail-vlasenko/chat-command.git
cd chat-command
sudo apt install python3-pip
pip3 install -r requirements.txt
export CHAT_COMMAND_PATH="$HOME/.chat_command"
export OPENAI_API_KEY="{os.getenv('OPENAI_API_KEY')}"
python3 setup.py --persistent --skip-alias
cd ..
rm -rf chat-command
source ~/.bashrc
echo -e "\nInstallation complete. You can now use the chat command. \\U1F916"
"""

if __name__ == "__main__":
    pyperclip.copy(INSTALL_STRING)
    print("📋 Installation string is copied to clipboard.")
