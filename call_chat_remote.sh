script_log=$(eval cat typescript | tail -n 20 | ansi2txt | col -b)

last_command=$1
shift 1

python3 "$CHAT_COMMAND_PATH"/basic_chat.py "$last_command" "$script_log" "$@"
