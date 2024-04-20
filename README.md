# `chat` command: your shell copilot

Do you sometimes forget how exactly to write a command in the terminal? 

Do your commands sometimes not work because an ubiquitous package is not installed, or a git repo is not initialized?

Then you are in the right place, as this simple command will offer a quick fix to your problems by using an LLM!

## Use cases

1. A command didn't work

```
~
❯ git push
fatal: not a git repository (or any of the parent directories): .git

~
❯ chat
Rerunning: git push
Attempting to fix the last command.
Select a command to execute:
1. git init
2. git remote add origin <repository_url>
3. git push origin master
Enter the index of the command to execute:
```

The script reruns[^1] the last command to obtain the output and act accordingly.

2. You forgot the exact command

```
~
❯ docker ps
CONTAINER ID   IMAGE                                         COMMAND                  CREATED        STATUS        PORTS     NAMES
9ae291b3886a   nvidia/cuda:11.3.1-cudnn8-devel-ubuntu18.04   "/opt/nvidia/nvidia_…"   39 hours ago   Up 38 hours             zealous_tesla

~
❯ chat "connect to docker"
Rerunning: docker ps
Generating suggestions based on the provided query.
Suggested command: docker exec -it zealous_tesla bash
Execute? ([y]/n)
(base) root@9ae291b3886a:/#
```

3. Many more features might be coming!

## Installation

1. Clone the repo
2. Set `$CHAT_COMMAND_PATH` (for example `export CHAT_COMMAND_PATH="$HOME/chat_command"`)
3. Run `install_chat_command.sh`
4. Add `source "$CHAT_COMMAND_PATH"/chat_wrapper.sh` (and the `export CHAT_COMMAND_PATH`) to your `.bashrc`
5. Obtain an OpenAI API key and add `export OPENAI_API_KEY="key"` to your `.bashrc`

[^1]: Because it is near-impossible to get the output of the previous commands in the shell
