function chat() {
    local clip_flag=""
    if [[ "$1" == "-c" ]]; then
        clip_flag="-c"
    fi

    local last_command=$(fc -ln -1)
    echo "Rerunning: $last_command"
    # Execute the last command and capture both stdout and stderr
    local output=$(eval "$last_command" 2>&1)

    python3 basic_chat.py $clip_flag "$last_command" "$output"

    # get the command from the file
    local command_file_path="$HOME/chat_command/command_to_execute.txt"
    if [[ -s "$command_file_path" ]]; then
        # Read the command from the file
        read -r command < "$command_file_path"
        eval "$command"

        # its single use
        rm -f "$command_file_path"
    else
        echo "No command to execute."
    fi
}
