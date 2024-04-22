import argparse


def main():
    BOLD = '\033[1m'
    RESET = '\033[0m'

    parser = argparse.ArgumentParser(prog="chat", description=f"The 🤖 {BOLD}chat{RESET} command CLI interface.")
    parser.add_argument("query", nargs='?', default="", help="Description of what needs to be done (optional)")
    parser.add_argument("-c", "--clipboard", action="store_true",
                        help="Include clipboard content in the prompt for suggestions")
    parser.add_argument("-n", "--no_rerun", action="store_true",
                        help="Do not rerun the last command")
    parser.add_argument("--with_context", action="store_true",
                        help="This is a follow-up request that provides context")
    args = parser.parse_args()

    def format_string(s):
        if not s:
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
