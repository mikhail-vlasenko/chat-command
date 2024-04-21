import os
import sys
import subprocess


def handle_marker(line):
    print(f"chat marker detected in line \"{line}\"")
    args = line.strip().split(' ')[1:]
    args.insert(0, 'ls')  # insert the last command
    print(f"args: {args}")
    args = ' '.join(args)
    subprocess.run([f"./call_chat_remote.sh {args}"])

    result_path = os.path.join(os.getenv("CHAT_COMMAND_PATH"), 'command_to_execute.txt')
    with open(result_path, "r") as f:
        print(f.read())


def main():
    try:
        while True:
            line = sys.stdin.readline()
            if 'chat_command_call' in line and 'chat_command_call $*' not in line:
                handle_marker(line)
            if not line:
                break
    except KeyboardInterrupt:
        print("Realtime processing of the chat command was interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
