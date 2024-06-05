import pyperclip
import os


INSTALL_STRING = f"""
if command -v sudo >/dev/null 2>&1; then
    SUDO=sudo
else
    SUDO=""
fi

$SUDO apt update &&
$SUDO apt install git-all &&
git clone https://github.com/mikhail-vlasenko/chat-command.git &&
cd chat-command &&
$SUDO apt install python3-pip &&
pip3 install -r requirements.txt &&
export CHAT_COMMAND_PATH="$HOME/.chat_command" &&
export OPENAI_API_KEY="{os.getenv('OPENAI_API_KEY')}" &&
python3 setup.py --persistent &&
cd .. &&
rm -rf chat-command &&
source ~/.bashrc &&
echo -e "\\n\\U1F680 Installation complete. You can now use the chat command. \\U1F916"
"""

if __name__ == "__main__":
    pyperclip.copy(INSTALL_STRING)
    print("📋 Installation string is copied to clipboard.")
