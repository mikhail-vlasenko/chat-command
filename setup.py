import os
import shutil
import re
import argparse
import sys


def check_and_set_chat_command_path(args_path):
    chat_command_path = os.getenv('CHAT_COMMAND_PATH')
    if args_path:
        chat_command_path = args_path

    if not chat_command_path:
        default_path = os.path.expanduser("~/.chat_command")
        chat_command_path = input(
            f"Define CHAT_COMMAND_PATH or Enter for [{default_path}]: ") or default_path
        os.environ['CHAT_COMMAND_PATH'] = chat_command_path

    if not os.path.exists(chat_command_path):
        os.makedirs(chat_command_path)
        os.makedirs(os.path.join(chat_command_path, "chat_history"))
    return chat_command_path


def copy_script_contents(chat_command_path):
    script_dir = os.path.dirname(os.path.realpath(__file__))

    def ignore_some_files(directory, contents):
        ignored = ['__pycache__']
        for filename in contents:
            if filename.startswith('.') or filename.endswith('.pyc'):
                ignored.append(filename)
        return ignored

    shutil.copytree(script_dir, chat_command_path, ignore=ignore_some_files, dirs_exist_ok=True)


def check_and_set_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("OPENAI_API_KEY is not set. Please provide it: ")
        os.environ['OPENAI_API_KEY'] = api_key
    return api_key


def update_shell_config(chat_command_path, api_key, persistent_flag=False):
    detected_profile_file = '~/.bashrc'
    if os.getenv('SHELL', '').endswith('zsh') and os.path.exists(os.path.expanduser('~/.zshrc')):
        detected_profile_file = '~/.zshrc'
    shell_config_options = {
        '1': detected_profile_file,
        '2': 'Enter custom path',
        '3': 'Skip this step (no persistent configuration)'
    }

    if persistent_flag:
        config_path = os.path.expanduser(shell_config_options['1'])
    else:
        print("Choose your shell configuration file for persistent installation:")
        for key, value in shell_config_options.items():
            print(f'{key}: {value}')
        choice = input("Your choice ([1]-3): ") or '1'
        if choice == '2':
            config_path = input("Enter the path to your shell configuration file: ")
            config_path = os.path.expanduser(config_path)
        elif choice == '3':
            return
        else:
            config_path = os.path.expanduser(shell_config_options.get(choice, ''))

    settings = [
        f'export CHAT_COMMAND_PATH="{chat_command_path}"',
        f'export CHAT_COMMAND_PYTHON="{sys.executable}"',
        f'source $CHAT_COMMAND_PATH"/chat_wrapper.sh"',
        f'export OPENAI_API_KEY="{api_key}"'
    ]

    with open(config_path, 'a+') as file:
        file.seek(0)
        existing_content = file.read()
        for setting in settings:
            if setting.startswith('export'):
                # Regular expression to check if the variable name is declared
                var_name = re.escape(re.split(r'[ =]', setting)[1])
                pattern = re.compile(r'^\s*export\s+' + var_name, re.MULTILINE)
            else:
                pattern = re.compile(re.escape(setting), re.MULTILINE)

            if not re.search(pattern, existing_content):
                file.write(setting + '\n')


def main():
    parser = argparse.ArgumentParser(description="Set up the chat command environment.")
    parser.add_argument("--chat_command_path",
                        help="Set the CHAT_COMMAND_PATH environment variable")
    parser.add_argument("--api_key",
                        help="Set the OPENAI_API_KEY environment variable")
    parser.add_argument("--persistent",
                        help="Automatically select the default shell configuration without prompt",
                        action='store_true')
    args = parser.parse_args()

    chat_command_path = check_and_set_chat_command_path(args.chat_command_path)
    copy_script_contents(chat_command_path)

    if args.api_key:
        api_key = args.api_key
        os.environ['OPENAI_API_KEY'] = api_key
    else:
        api_key = check_and_set_api_key()

    update_shell_config(chat_command_path, api_key, args.persistent)
    print(f'Installation complete. '
          f'You may need to restart your shell or run\n'
          f'source "{chat_command_path}/chat_wrapper.sh"\n'
          f'to use the \033[1m\033[4mchat\033[0m command. '
          f'Consider \033[1m\033[4mchat -h\033[0m for more information.')


if __name__ == "__main__":
    main()
