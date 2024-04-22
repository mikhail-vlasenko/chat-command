function chat() {
    contains_help_flag() {
        for arg in "$@"; do
            if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
                return 0  # True, help flag found
            fi
        done
        return 1  # False, help flag not found
    }
    # Check if the help option is present
    if contains_help_flag "$@"; then
        # Display the help message (not let it get consumed by bash)
        $CHAT_COMMAND_PYTHON "$CHAT_COMMAND_PATH"/handle_cli_args.py "$@"
        return
    else
        # delegate argument parsing to an actual programming language
        all_args=$($CHAT_COMMAND_PYTHON "$CHAT_COMMAND_PATH"/handle_cli_args.py "$@")
        # Set IFS to tab to split the output properly (newline just refuses to work for some reason)
        IFS=$'\t'
        # Read the output into separate variables
        read -r query clipboard no_exec with_context <<< "$all_args"
    fi

    local last_command=$(fc -ln -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//') # Trim whitespaces
    local output="<output is not available>"

    # Check if the last command starts with "chat "
    if [[ "$last_command" =~ ^[[:space:]]*chat[[:space:]] ]]; then
        echo "⏭️ Refusing to rerun 'chat' command."
    # Check if the last command is the same as the last command suggested and executed by 'chat',
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
            if ! $no_exec; then
                echo "🔄 This command was executed $count times in the last 5 commands, rerunning."
                local output=$(eval "$last_command" 2>&1)
            fi
        fi
    else
        # skip this if flag -n is passed
        if ! $no_exec; then
            echo "🔄 Rerunning: $last_command"
            # Execute the last command and capture both stdout and stderr
            local output=$(eval "$last_command" 2>&1)
        fi
    fi

    # Pass all arguments to the Python script along with last command and its output
    $CHAT_COMMAND_PYTHON "$CHAT_COMMAND_PATH"/basic_chat.py "$last_command" "$output" "$query" "$clipboard" "$with_context"

    # get the command to be executed from the file
    local command_file_path="$CHAT_COMMAND_PATH/command_to_execute.txt"
    if [[ -s "$command_file_path" ]]; then
        # Open the file descriptor (using descriptor 3 as its right after the standard ones)
        exec 3< "$command_file_path"
        # Read the command from the first line
        read -r command <&3
        # Read the conversation id from the second line (can be used by next requests in this session)
        export CHAT_COMMAND_CONV_ID=""
        read -r CHAT_COMMAND_CONV_ID <&3
        # Read whether the command is for context or not
        local command_context_flag
        read -r command_context_flag <&3
        # Close the file descriptor
        exec 3<&-

        # Add the command to the history
        if [[ -n $ZSH_VERSION ]]; then
            # Zsh-specific command (i hate that i have to do it this way)
            print -s "$command"
        else
            # Bash or other shell command
            history -s "$command"
        fi

        eval "$command" | tee /tmp/chat_command_output.txt
        export CHAT_COMMAND_LAST_COMMAND="$command"
        export CHAT_COMMAND_LAST_OUTPUT=$(col -b < /tmp/chat_command_output.txt)

        # its single use
        rm -f "$command_file_path"

        if [[ "$command_context_flag" -eq 1 ]]; then
            # the previous command was for context, so once it was obtained,
            # we can save the user calling chat again.
            # The environment variables will allow chat to see the result.
            echo "📝 Context obtained, calling chat again."
            chat -n --with_context
        fi
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

