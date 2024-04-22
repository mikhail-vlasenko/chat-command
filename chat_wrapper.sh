function chat() {
    local last_command=$(fc -ln -1)

    # Check if the last command starts with "chat "
    if [[ "$last_command" =~ ^[[:space:]]*chat[[:space:]] ]]; then
        echo "⏭️ Refusing to rerun 'chat' command."
        local last_command=""
        local output=""
    # Check if the last command is the same as the last executed chat_command,
    # and it is not run often (more than once in the last 5 commands).
    # Then, we can skip it
    elif [[ "$last_command" == "$CHAT_COMMAND_LAST_COMMAND" ]]; then
        # Fetch the last 5 commands from history excluding the very last one
        local recent_commands=$(fc -ln -5)  # Get last 5
        # Count occurrences of the last command in recent commands
        local count=$(grep -cFx "$last_command" <<< "$recent_commands")

        if [[ $count == 1 ]]; then
            echo "⏭️ This command was the last executed by 'chat', skipping rerun."
            local output=""
        else
            echo "🔄 This command was executed $count times in the last 5 commands, rerunning."
            local output=$(eval "$last_command" 2>&1)
        fi
    else
        echo "🔄 Rerunning: $last_command"
        # Execute the last command and capture both stdout and stderr
        local output=$(eval "$last_command" 2>&1)
    fi

    echo "🤖 Querying the model..."
    # Pass all arguments to the Python script along with last command and its output
    $CHAT_COMMAND_PYTHON "$CHAT_COMMAND_PATH"/basic_chat.py "$last_command" "$output" "$@"

    # get the command to be executed from the file
    local command_file_path="$CHAT_COMMAND_PATH/command_to_execute.txt"
    if [[ -s "$command_file_path" ]]; then
        # Open the file descriptor (using descriptor 3 as its right after the standard ones)
        exec 3< "$command_file_path"
        # Read the chat_command from the first line
        read -r chat_command <&3
        # Read the conversation id from the second line (can be used by next requests in this session)
        export CHAT_COMMAND_CONV_ID=""
        read -r CHAT_COMMAND_CONV_ID <&3
        # Close the file descriptor
        exec 3<&-

        # Add the command to the history
        if [[ -n $ZSH_VERSION ]]; then
            # Zsh-specific command (i hate that i have to do it this way)
            print -s "$chat_command"
        else
            # Bash or other shell command
            history -s "$chat_command"
        fi

        eval "$chat_command" | tee /tmp/output.txt
        export CHAT_COMMAND_LAST_COMMAND="$chat_command"
        export CHAT_COMMAND_LAST_OUTPUT=$(< /tmp/output.txt)

        # its single use
        rm -f "$command_file_path"
    else
        echo "❌ No command to execute."
    fi
}

function chatNewSession() {
    # Start a new session by removing the conversation id
    export CHAT_COMMAND_CONV_ID=""
    export CHAT_COMMAND_LAST_COMMAND=""
    export CHAT_COMMAND_LAST_OUTPUT=""
    echo "♻️ Started a new chat session."
}

function chatInstall() {
    $CHAT_COMMAND_PYTHON "$CHAT_COMMAND_PATH"/quick_install.py
}

function chatHistory() {
    less <<< "$(eval "$CHAT_COMMAND_PYTHON $CHAT_COMMAND_PATH/read_history.py")"
}

