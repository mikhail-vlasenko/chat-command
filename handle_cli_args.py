import argparse

from config import Config, BOLD, RESET, UNDERLINE


def main():
    parser = argparse.ArgumentParser(
        prog="chat",
        description=
        f"The 🤖 {BOLD}{UNDERLINE}chat{RESET} command CLI interface.\n\n"
        f"The command allows you get suggestions and fixes from an LLM right in your shell. "
        f"If a command that you ran failed, you can just run {BOLD}{UNDERLINE}chat{RESET}, "
        f"and it will quickly suggest a command that fixes the issue! "
        f"Alternatively, if you are not sure what precise command you need to do a thing, "
        f"run {BOLD}{UNDERLINE}chat \"your query\"{RESET} and receive suggestions!\n\n"
        f"When you are presented with a choice of whether to apply a suggestion, "
        f"note the {BOLD}<new instructions>{RESET} option. "
        f"You can use it in case neither of the suggestions are to your liking, "
        f"simply typing in a string instead of the command selection. "
        f"This string will be passed to the LLM as new instructions, and the model will produce new suggestions.\n\n"
        f"This is the primary command, but the tool also includes:\n"
        f"1. {BOLD}{UNDERLINE}chatNewSession{RESET}, which resets the conversation history.\n"
        f"2. {BOLD}{UNDERLINE}chatInstall{RESET}, which copies an express installation string to your clipboard. "
        f"This can be useful when you just logged into a new machine or a docker container.\n"
        f"3. {BOLD}{UNDERLINE}chatHistory{RESET}, which lets you inspect you current conversation in full.\n",
        epilog=Config.configuration_help_string() +
               "\n🌟 Don't forget to star the project on GitHub if you like it!\n"
               "https://github.com/mikhail-vlasenko/chat-command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("query", nargs='?', default="", help="Description of what needs to be done (optional)")
    parser.add_argument("-c", "--clipboard", action="store_true",
                        help="Include clipboard content in the prompt for suggestions")
    parser.add_argument("-n", "--no_rerun", action="store_true",
                        help="Do not rerun the last command")
    parser.add_argument("--with_context", action="store_true",
                        help="This is a follow-up request that provides context to the previous interaction")
    args = parser.parse_args()

    def format_string(s):
        if not s:
            # empty strings mess up parsing
            return "\"\""
        return s.replace("\t", "\\t")

    # Output all arguments back to the shell, separated by tabs so that they can be easily parsed
    print(format_string(args.query), end='\t')
    # convert to ints to avoid dealing with truthy values
    print(int(args.clipboard), end='\t')
    print('true' if args.no_rerun else 'false', end='\t')
    print(int(args.with_context), end='\t')


if __name__ == "__main__":
    main()
