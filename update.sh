cd .. &&
git clone https://github.com/mikhail-vlasenko/chat-command.git &&
cd chat-command &&
pip3 install -r requirements.txt &&
python3 setup.py --persistent &&
cd .. &&
rm -rf chat-command &&
echo "🚀 Chat command installed successfully! Please restart your terminal."
