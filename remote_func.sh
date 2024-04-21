chat2() {
    echo "chat_command_call $*"
    fc -ln -1
    read command
    history -s "$command"
    eval "$command"
}
