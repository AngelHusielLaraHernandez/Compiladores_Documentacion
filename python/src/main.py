import os
import sys
from file_handler import read_file, export_tokens
from lexer import tokenize_code
from formatter import print_tokens_table, print_grouped_tokens, print_colored_code, group_tokens
from colorama import init, Fore, Style

# Initialize colorama to enable colors in the terminal
init(autoreset=True)

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def read_keyboard():
    print("\n" + "=" * 40)
    print(Style.BRIGHT+ "\t   Keyboard Input" + Style.RESET_ALL)
    print("=" * 40)
    print("\nWrite your source code in C language")
    print(Fore.BLUE + "NOTE: When you are done, type" + Fore.RED + " '$' " + Fore.BLUE + "to finish the input.\n")

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break

        # $ it is the terminal symbol to end the input, if it detects it, it stops reading from keyboard
        if "$" in line:
            before_symbol = line.split("$", 1)[0]
            if before_symbol:
                lines.append(before_symbol)
            break

        lines.append(line)

    return "\n".join(lines)


def ask(message):
    while True:
        r = input(f"{message} (y/n): ").strip().lower()
        if r in ("y", "n"):
            return r
        print(Fore.YELLOW + "Invalid Option. Enter 'y' or 'n'")


def ask_input():
    while True:
        print("\nSelect the input source mode:")
        print("[ 1 ] File")
        print("[ 2 ] Keyboard")
        print("[ 3 ] Quit")
        op = input("\n> Option: ").strip()

        if op in ("1", "2", "3"):
            return op
        
        print(Fore.YELLOW + "Invalid Option. Try again")


def load_source_file(project_root, path_from_user=None):
    if not path_from_user:
        path_from_user = input("> File Name: ").strip()

    # Normalization of  the path
    if os.path.isabs(path_from_user):
        input_path = path_from_user
    else:
        # Reading the file from the "inputs" folder
        input_path = os.path.join(project_root, "inputs" ,path_from_user)
    
    source_code, error = read_file(input_path)

    if not source_code:
        print(Fore.RED + "Error: " + error)
        return None, None, None

    file_name = os.path.basename(input_path)
    base_name = os.path.splitext(file_name)[0]
    output_file = os.path.join(project_root, "outputs", f"{base_name}_output.txt")
    return source_code, file_name, output_file


def process_analysis(source_code, file_name, output_file):
    tokens = tokenize_code(source_code)
    # Case: If no tokens were found
    if not tokens:
        print(Fore.YELLOW + "No valid tokens were found in the file.")
        return

    print("\n" + "=" * 50)
    print(Style.BRIGHT+ "\t   Lexical Analysis of <" + file_name + ">\n" + Style.RESET_ALL)
    print("=" * 50)

    print_tokens_table(tokens)

    if ask("> Do you want to see the grouped tokens by type?") == "y":
        print_grouped_tokens(tokens)

    if ask("> Do you want to see  the original code with the tokens highlighted?") == "y":
        print_colored_code(source_code)

    if ask("> Do you want to export the results?") == "y":
        grouped_data = group_tokens(tokens)
        e = export_tokens(tokens, output_file, grouped_data)
        if e is None:
            print(Fore.GREEN + f"Results exported successfully to: {output_file}")
        else:
            print(Fore.RED + f"Error exporting the file: {e}")

def main():
    # Get the proyect path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    # Check if a file name was provided as a command-line argument
    file_arg = sys.argv[1] if len(sys.argv) >= 2 else None

    # If a file name was provided as an argument, we load it directly
    if file_arg:
        source_code, file_name, output_file = load_source_file(project_root, file_arg)
        file_arg = None
    else:
        source_code = read_keyboard()
        if not source_code.strip():
            print(Fore.RED + "Not source code entered. Analysis canceled")
            source_code, file_name, output_file = None, None, None
        else:
            file_name = "keyboard_input"
            output_file = os.path.join(project_root, "outputs", "keyboard_output.txt")

    if source_code:
        process_analysis(source_code, file_name, output_file)

    # End of the first analysis
    while True:
        if ask("\nWould you like to run a new analysis?") == "n":
            break

        # Menu for selecting the input mode for the new analysis
        mode = ask_input()
        clear_terminal()

        if mode == "1":
            source_code, file_name, output_file = load_source_file(project_root)
            if source_code:
                process_analysis(source_code, file_name, output_file)

        elif mode == "2":
            source_code = read_keyboard()
            if not source_code.strip():
                print(Fore.RED + "Not source code entered. Analysis canceled")
            else:
                file_name = "keyboard_input"
                output_file = os.path.join(project_root, "outputs", "keyboard_output.txt")
                process_analysis(source_code, file_name, output_file)
        else:
            break

if __name__ == "__main__":
    main()