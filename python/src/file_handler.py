import os

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read(), None
    except FileNotFoundError:
        return "", f"The file '{file_path}' was not found"
    except Exception as e:
        return "", str(e)

def export_tokens(tokens, output_path, grouped_tokens):
    try:
        # Verify if the directory exists, if not, create it
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            # TABLE
            f.write("Lexical Analysis - Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"{'TOKEN TYPE':<20} | {'LEXEMS'}\n")
            f.write("-" * 50 + "\n")

            f.write(f"Total tokens found: {len(tokens)}\n\n\n")
            for token_type, value in tokens:
                # Cleaning newlines for better readability in the output file
                clean_value = value.replace('\n', '\\n').replace('\r', '\\r')
                f.write(f"{token_type:<20} | {clean_value}\n")

            f.write("=" * 50 + "\n")

            # GROUPED BY TYPE
            f.write("GROUPED TOKENS BY TYPE\n")
            f.write("=" * 50 + "\n")

            for category, token_counts in grouped_tokens.items():
                if token_counts:
                    total_in_category = sum(token_counts.values())
                    f.write(f"{category} (Total: {total_in_category}):\n")
                    
                    for token, count in token_counts.items():
                        f.write(f"    {token}: {count}\n")
                    
                    f.write("\n")
            f.write(f"Total tokens found: {len(tokens)}\n\n\n")
            return None

    except Exception as e:
        return str(e)