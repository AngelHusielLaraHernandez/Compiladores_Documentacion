# C-RELOAD: A Syntax and Semantic Analyzer for C Language (Terminal Version)
import os
import sys
from colorama import init, Fore, Style

# Project structure setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Imports from your modules
from utils.file_handler import read_file, export_tokens, export_ast_json
from compiler.lexer import tokenize_code
from utils.formatter import print_tokens_table, print_grouped_tokens, print_colored_code, group_tokens
from compiler.parser_sdt import parse_source

# Initialize colorama to enable colors in the terminal
init(autoreset=True)

def print_header():
    l1 = "  ___      ____  _____ _      ___    _    ____  "
    l2 = " / __\ __ |  _ \| ____| |    / _ \  / \  |  _ \ "
    l3 = "| |   |__|| |_) |  _| | |   | | | |/ _ \ | | | |"
    l4 = "| |__ |__||  _ <| |___| |___| |_| / ___ \| |_| |"
    l5 = " \___/    |_| \_\_____|_____|\___/_/   \_\____/ "

    print(Fore.WHITE + Style.BRIGHT + l1)
    print(Fore.WHITE + Style.BRIGHT + l2)
    print(Fore.BLUE + Style.BRIGHT + l3)
    print(Fore.BLUE + Style.BRIGHT + l4)
    print(Fore.BLUE + Style.BRIGHT + l5)
    print(Fore.CYAN + Style.BRIGHT + " " * 12 + "Syntax & Semantic Analyzer")
    print(Style.DIM + "-" * 55 + "\n")

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def read_keyboard():
    print("\n" + "=" * 40)
    print(Style.BRIGHT + "\t   Keyboard Input" + Style.RESET_ALL)
    print("=" * 40)
    print("\nWrite your source code in C language")
    print(Fore.BLUE + "NOTE: Type " + Fore.RED + "'$'" + Fore.BLUE + " on a new line to finish.\n")

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
        input_path = os.path.join(project_root, "inputs", path_from_user)
    
    source_code, error = read_file(input_path)
    if not source_code:
        print(Fore.RED + "Error: " + error)
        return None, None, None

    file_name = os.path.basename(input_path)
    base_name = os.path.splitext(file_name)[0]
    output_file = os.path.join(project_root, "outputs", f"report_{base_name}.txt")
    return source_code, file_name, output_file

def process_analysis(source_code, file_name, output_file):
    tokens = tokenize_code(source_code)
    analysis_result = None
    # Case: If no tokens were found
    if not tokens:
        print(Fore.YELLOW + "No valid tokens found.")
        return

    print("\n" + "=" * 50)
    print(Style.BRIGHT + f"\tLexical Analysis of <{file_name}>\n" + Style.RESET_ALL)
    print("=" * 50)
    print_tokens_table(tokens)

    if ask("> Run syntax and semantic analysis?") == "y":
        analysis_result = parse_source(source_code)
        
        # Syntax Result
        if analysis_result["syntax_ok"]:
            print(Fore.GREEN + "Syntax analysis: VALID")
        else:
            print(Fore.RED + "Syntax analysis: INVALID")
            for err in analysis_result["syntax_errors"]:
                print(Fore.RED + f"  - {err}")
            print(Fore.RED + "Semantic analysis (SDT): INVALID")
            

        # Semantic Result
        if analysis_result["syntax_ok"]:
            if analysis_result["semantic_ok"]:
                print(Fore.GREEN + "Semantic analysis (SDT): VALID")
            else:
                print(Fore.RED + "Semantic analysis (SDT): INVALID")
                for err in analysis_result["semantic_errors"]:
                    print(Fore.RED + f"  - {err}")

    if ask("> View tokens grouped by type?") == "y":
        print_grouped_tokens(tokens)

    if ask("> View highlighted source code?") == "y":
        print_colored_code(source_code)

    if ask("> Export analysis results?") == "y":
        if analysis_result is None:
            analysis_result = parse_source(source_code)

        # 1. Export Text Report
        grouped_data = group_tokens(tokens)
        e = export_tokens(tokens, output_file, grouped_data, analysis_result)
        if e is None:
            print(Fore.GREEN + f"Text report exported: {output_file}")
        else:
            print(Fore.RED + f"Text export error: {e}")

        # 2. Export AST JSON (Only if syntax is valid)
        if analysis_result["syntax_ok"] and analysis_result["ast_dict"]:
            json_file = output_file.replace(".txt", ".json").replace("report_", "ast_")
            je = export_ast_json(analysis_result["ast_dict"], json_file)
            if je is None:
                print(Fore.GREEN + f"AST JSON exported: {json_file}")
            else:
                print(Fore.RED + f"JSON export error: {je}")

def main():
    project_root = PROJECT_ROOT
    # Check if a file name was provided as a command-line argument
    file_arg = sys.argv[1] if len(sys.argv) >= 2 else None

    while True:
        clear_terminal()
        print_header()

        # If a file name was provided as an argument, we load it directly
        if file_arg:
            source_code, file_name, output_file = load_source_file(project_root, file_arg)
            file_arg = None
        else:
            mode = ask_input()
            if mode == "1":
                source_code, file_name, output_file = load_source_file(project_root)
            elif mode == "2":
                source_code = read_keyboard()
                file_name = "keyboard_input"
                output_file = os.path.join(project_root, "outputs", "report_keyboard.txt")
            else:
                break

        if source_code and source_code.strip():
            process_analysis(source_code, file_name, output_file)
        elif source_code:
            print(Fore.RED + "Not source code entered. Analysis canceled.")

        if ask("\nRun a new analysis?") == "n":
            break

if __name__ == "__main__":
    main()