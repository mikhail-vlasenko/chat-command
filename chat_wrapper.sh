function chat() {
    local last_command=$(fc -ln -1)
    echo "Rerunning: $last_command"
    # Execute the last command and capture both stdout and stderr
    local output=$(eval "$last_command" 2>&1)

    # Pass all arguments to the Python script along with last command and its output
    python3 basic_chat.py "$last_command" "$output" "$@"

    # get the command from the file
    local command_file_path="$HOME/chat_command/command_to_execute.txt"
    if [[ -s "$command_file_path" ]]; then
        # Read the command from the file
        read -r command < "$command_file_path"

        # Add the command to the history
        if [[ -n $ZSH_VERSION ]]; then
            # Zsh-specific command (i hate that i have to do it this way)
            print -s "$command"
        else
            # Bash or other shell command
            history -s "$command"
        fi

        eval "$command"

        # its single use
        rm -f "$command_file_path"
    else
        echo "No command to execute."
    fi
}
