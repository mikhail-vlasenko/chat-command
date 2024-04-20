import pyperclip
import os


INSTALL_STRING = f"""sudo apt update
sudo apt install git-all
git clone https://github.com/mikhail-vlasenko/chat-command.git
cd chat-command
sudo apt install python3-pip
pip3 install -r requirements.txt
export CHAT_COMMAND_PATH="$HOME/chat_command"
source install_chat_command.sh
echo "export CHAT_COMMAND_PATH="$HOME/chat_command"" >> ~/.bashrc
echo "source "$CHAT_COMMAND_PATH"/chat_wrapper.sh" >> ~/.bashrc
echo "export OPENAI_API_KEY="{os.getenv('OPENAI_API_KEY')}" >> ~/.bashrc
source ~/.bashrc
echo "Installation complete. You can now use the chat command." """

if __name__ == "__main__":
    pyperclip.copy(INSTALL_STRING)
