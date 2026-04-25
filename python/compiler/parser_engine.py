# Module that combines the entire parsing and semantic analysis process
from typing import Any, Dict, List

import ply.yacc as yacc

from .adapter import PlyLexerAdapter
from .grammar import GrammarRules
from .lexer import tokenize_code
from .semantic import analyze_semantics

# Heriting from GrammarRules to access production rules and precedence
class ParserSDT(GrammarRules):
    def __init__(self) -> None:
        self.syntax_errors: List[str] = []
        # Create the LALR(1) parser using PLY.YACC with the production rules defined in GrammarRules
        self.parser = yacc.yacc(module=self, start="program", write_tables=False, debug=False)

    def parse(self, source_code: str) -> Dict[str, Any]:
        self.syntax_errors = []
        # Tokenize the source code using the lexer defined in lexer.py
        token_list = tokenize_code(source_code)
        # Create an adapter to convert the list of tokens into the format expected by PLY.YACC 
        adapter = PlyLexerAdapter(token_list, source_code=source_code)
        # Parse the tokens to generate the AST, while collecting syntax errors if any
        ast = self.parser.parse(lexer=adapter)

        result: Dict[str, Any] = {
            "tokens": token_list,
            "syntax_ok": len(self.syntax_errors) == 0 and ast is not None,
            "syntax_errors": self.syntax_errors,
            "ast": ast,
            "ast_dict": ast.to_dict() if ast else None,
            "ast_tree": "\n".join(ast.to_tree_lines()) if ast else "",
            "semantic_ok": False,
            "semantic_errors": [],
            "symbol_table": {},
            "sdt_trace": [],
        }

        if result["syntax_ok"]:
            # If syntax is valid, proceed to semantic analysis using the AST generated.
            semantic_ok, semantic_errors, symbol_table, sdt_trace = analyze_semantics(ast)
            result["semantic_ok"] = semantic_ok
            result["semantic_errors"] = semantic_errors
            result["symbol_table"] = symbol_table
            result["sdt_trace"] = sdt_trace

        return result

def parse_source(source_code: str) -> Dict[str, Any]:
    parser = ParserSDT()
    return parser.parse(source_code)
