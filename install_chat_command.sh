if [ -z "${CHAT_COMMAND_PATH}" ]; then
    echo "Please set CHAT_COMMAND_PATH before running this script. This will be the installation path"
    exit 1
fi

mkdir -p "$CHAT_COMMAND_PATH"

cp chat_wrapper.sh "$CHAT_COMMAND_PATH"
cp basic_chat.py "$CHAT_COMMAND_PATH"
cp examples.py "$CHAT_COMMAND_PATH"
cp quick_install.py "$CHAT_COMMAND_PATH"

echo "Installed chat command to $CHAT_COMMAND_PATH"
