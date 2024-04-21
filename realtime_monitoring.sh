#!/bin/bash

# script -f | tee /dev/tty | ./realtime_monitoring.sh
# docker exec -it zealous_tesla bash
# define chat
# ls
# chat

# Function to handle the marker
handle_marker() {
    local line="$1"
    echo "chat marker detected in line \"$line\""

    # Extract arguments from the line, assuming 'chat_command_call' is followed by the arguments
    local args=(${line#*chat_command_call })

    # Run a command with these arguments
    ./call_chat_remote.sh "${args[@]}"

    # Assuming CHAT_COMMAND_PATH is set in your environment and points to the directory
    local result_path="${CHAT_COMMAND_PATH}/command_to_execute.txt"
    if [[ -f "$result_path" ]]; then
        cat "$result_path"
    else
        echo "No command file found."
    fi
}

# Main loop to process input lines
while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" == *"chat_command_call"* && "$line" != *"chat_command_call \$*"* ]]; then
        handle_marker "$line"
    fi
done

# Handle user interrupt (Ctrl+C) and other potential errors
trap 'echo "Realtime processing of the chat command was interrupted by user"; exit' INT
trap 'echo "Error occurred"; exit 1' ERR
