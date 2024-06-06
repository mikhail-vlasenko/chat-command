# `chat` command: your shell copilot

Do you sometimes forget how exactly to write a command in the terminal? 

Do your commands sometimes not work because a ubiquitous package is not installed, or a git repo is not initialized?

Then you are in the right place, as this simple command will offer a quick fix to your problems by using an LLM!

## Usage

1. Call `chat` after a command that didn't work, and it will provide potential fixes

```
$ git push
fatal: not a git repository (or any of the parent directories): .git

$ chat
🔄 Rerunning: git push
🤖 Generating suggestions based on the provided query...
ℹ️ Suggested command: git init
❔ Execute? ([y]/n/<new instructions>):
```

The script reruns[^1] the last command to obtain the output and act accordingly.

2. You know what you are doing, but forgot the exact command

```
$ chat "bash into docker container"
⏭️ This command was the last executed by 'chat', skipping rerun.
🤖 Generating suggestions based on the provided query...
ℹ️ Suggested command: docker ps # for context
❔ Execute? ([y]/n/<new instructions>):
CONTAINER ID   IMAGE        COMMAND                  CREATED        STATUS       PORTS                    NAMES
f89482811c21   g_grouping   "/opt/nvidia/nvidia_…"   35 hours ago   Up 7 hours   0.0.0.0:5000->5000/tcp   boring_black
📝 Context obtained, calling chat again.
🤖 Analyzing the context...
ℹ️ Suggested command: docker exec -it boring_black bash
❔ Execute? ([y]/n/<new instructions>):
(gaussian_grouping) root@f89482811c21:/#


$ chat "is apache active?"
🔄 Rerunning: tmux
🤖 Generating suggestions based on the provided query...
ℹ Suggested command: systemctl status apache2.service # for context
❔ Execute? ([y]/n/<new instructions>):
○ apache2.service - The Apache HTTP Server
     Loaded: loaded (/lib/systemd/system/apache2.service; disabled; vendor preset: enabled)
     Active: inactive (dead)
       Docs: https://httpd.apache.org/docs/2.4/
📝 Context obtained, calling chat again.
🤖 Analyzing the context...
ℹ️ Suggested command: The Apache service is currently inactive (dead).
```

Notice that `chat` first obtains necessary context, and only then proceeds to fulfill the request. 
Also, all `# for context` commands automatically trigger `chat` again, so that you don't have to!

3. Many more features might be coming!

## Installation

1. `git clone https://github.com/mikhail-vlasenko/chat-command.git && cd chat-command`
2. `pip3 install -r requirements.txt`
3. `python3 setup.py`
4. Restart your shell

[^1]: Because it is near-impossible to get the output of the previous commands in the shell
