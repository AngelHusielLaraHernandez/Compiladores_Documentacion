# C-Reload: Syntax & Semantic Analyzer (UI)

import json
import os
import sys

import streamlit as st

# Adding the project root to sys.path to allow imports from the compiler and utils packages

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
	sys.path.append(ROOT_DIR)

from compiler.parser_sdt import parse_source

# Files for sample code (located in /inputs)
SAMPLE_FILES = {
    "OK - Semantic rules": "ok_reglas_semanticas.c",
    "SYN - Invalid syntax": "syn_sintaxis_invalida.c",
    "SYN - If without parentheses": "syn_if_sin_parentesis.c",
    "SEM - Undeclared variable": "sem_variable_no_declarada.c",
    "SEM - Incompatible assignment": "sem_asignacion_incompatible.c",
    "SEM - Invalid operators": "sem_operadores_invalidos.c",
    "SEM - Invalid printf arguments": "sem_printf_argumentos_invalidos.c",
    "SEM - Incompatible scanf format": "sem_scanf_formato_incompatible.c",
    "SEM - Non-evaluable condition": "sem_condicion_no_evaluable.c",
}


def _read_sample_file(file_name: str) -> str:
    file_path = os.path.join(ROOT_DIR, "inputs", file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as sample_file:
            return sample_file.read()
    except OSError:
        return f"/* Failed to load sample: {file_name} */\n"


def _build_sample_code() -> dict:
	return {label: _read_sample_file(file_name) for label, file_name in SAMPLE_FILES.items()}


SAMPLE_CODE = _build_sample_code()
DEFAULT_SAMPLE_KEY = next(iter(SAMPLE_CODE), "")


def _load_css() -> None:
	css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
	if os.path.exists(css_path):
		with open(css_path, "r", encoding="utf-8") as css_file:
			st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Component for displaying the syntax and semantic status in a visually appealing way
def _status_block(syntax_ok: bool, semantic_ok: bool) -> None:
	syntax_class = "ok" if syntax_ok else "fail"
	syntax_text = "YES" if syntax_ok else "NO"

	sdt_ok = syntax_ok and semantic_ok
	sdt_class = "ok" if sdt_ok else "fail"
	if syntax_ok:
		sdt_text = "YES" if semantic_ok else "NO"
	else:
		sdt_text = "NO"

	st.markdown(
		f'''
		<div class="status-grid">
			<div class="status-card {syntax_class}">
                <div class="status-title">Valid Syntax</div>
				<div class="status-value">{syntax_text}</div>
			</div>
			<div class="status-card {sdt_class}">
                <div class="status-title">Valid SDT</div>
				<div class="status-value">{sdt_text}</div>
			</div>
		</div>
		''',
		unsafe_allow_html=True,
	)

# Formatting tokens in the console
def _tokens_as_table(tokens):
	return [
        {"category": category, "lexeme": value}
		for category, value in tokens
	]

# Generates a DOT graph from the AST dictionary.
def _ast_to_dot(ast_dict, rankdir="TB"):
	if not ast_dict:
		return "digraph AST { label=\"AST\"; }"

	nodes = []
	edges = []
	count = 0

	def esc(value):
		return str(value).replace('"', '\\"').replace("<", "&lt;").replace(">", "&gt;")

	def node_style(kind):
		if kind in {"if", "if_else", "while", "for", "block"}:
			return "#FFF4CE", "#B08900"
		if kind in {"declaration", "declaration_list", "assignment", "return"}:
			return "#DFF6DD", "#2E7D32"
		if kind in {"binary_op", "unary_op", "identifier", "constant", "literal"}:
			return "#DDEBFF", "#1E5AA8"
		return "#F3F2F1", "#605E5C"

	def walk(node, parent_id=None):
		nonlocal count
		count += 1
		node_id = f"n{count}"
		kind = node.get("kind", "node")
		value = node.get("value")
		lineno = node.get("lineno", 0)
		fill, border = node_style(kind)

		value_text = "-" if value is None else esc(value)
		if len(value_text) > 42:
			value_text = value_text[:39] + "..."
		line_text = f"L{lineno}" if lineno else "-"

		label = (
			"<"
			"<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLPADDING=\"2\">"
			f"<TR><TD><B>{esc(kind)}</B></TD></TR>"
			f"<TR><TD ALIGN=\"LEFT\"><FONT POINT-SIZE=\"10\">value: {value_text}</FONT></TD></TR>"
			f"<TR><TD ALIGN=\"LEFT\"><FONT POINT-SIZE=\"10\">line: {line_text}</FONT></TD></TR>"
			"</TABLE>>"
		)

		nodes.append(
			f"{node_id} [label={label}, shape=box, style=\"rounded,filled\", fillcolor=\"{fill}\", color=\"{border}\", penwidth=1.4]"
		)
		if parent_id is not None:
			edges.append(f"{parent_id} -> {node_id} [color=\"#8A8886\", arrowsize=0.7]")

		for child in node.get("children", []):
			walk(child, node_id)

	walk(ast_dict)
	body = "\n".join(nodes + edges)
	return (
		"digraph AST {\n"
		f"rankdir={rankdir};\n"
		"nodesep=0.25;\n"
		"ranksep=0.35;\n"
		"fontname=\"Segoe UI\";\n"
		"node [fontname=\"Segoe UI\"];\n"
		f"{body}\n"
		"}\n"
	)


def main() -> None:
    st.set_page_config(page_title="Syntax & Semantic Analyzer", page_icon="C", layout="wide")
    _load_css()

    # Initialization of session state variables
    if "source_code" not in st.session_state:
        st.session_state["source_code"] = SAMPLE_CODE[DEFAULT_SAMPLE_KEY]
    if "sample_choice" not in st.session_state:
        st.session_state["sample_choice"] = DEFAULT_SAMPLE_KEY
    if st.session_state["sample_choice"] not in SAMPLE_CODE:
        st.session_state["sample_choice"] = DEFAULT_SAMPLE_KEY
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None

    def _on_sample_change() -> None:
        selected = st.session_state["sample_choice"]
        st.session_state["source_code"] = SAMPLE_CODE[selected]
        st.session_state["analysis_result"] = None

	# Titles
    st.markdown('<div class="project-title">C-Reload</div>', unsafe_allow_html=True)
    st.title("Syntax & Semantic Analyzer")

    # Layout: Two columns (Input | Output)
    input_col, output_col = st.columns([1.1, 1.5], gap="large")

    with input_col:
        st.subheader("Input")
        
		# Sample selection dropdown
        st.selectbox(
            "Samples",
            list(SAMPLE_CODE.keys()),
            key="sample_choice",
            on_change=_on_sample_change,
        )

        # Source code text area
        text_container = st.container()

        # Buttons for file upload and analysis
        col_btn_analizar, col_btn_upload = st.columns(2, gap="small")
        
        with col_btn_upload:
            uploaded = st.file_uploader("Upload", type=["c", "txt"], label_visibility="collapsed")
            
		# Logic to handle file upload and update the text area with the uploaded content
        if uploaded is not None:
            uploaded_text = uploaded.getvalue().decode("utf-8", errors="ignore")
            if uploaded_text != st.session_state.get("last_uploaded_content", ""):
                st.session_state["source_code"] = uploaded_text
                st.session_state["last_uploaded_content"] = uploaded_text
                st.session_state["analysis_result"] = None
                
        with text_container:
            st.text_area("C source code", height=300, key="source_code")

        with col_btn_analizar:
            if st.button("Analyze", type="primary", use_container_width=True):
                st.session_state["analysis_result"] = parse_source(st.session_state["source_code"])


    with output_col:
        st.subheader("Output")
        result = st.session_state.get("analysis_result")
        if result is None:
            st.info("Select or edit a sample on the left, then click Analyze.")
        else:
            _status_block(result["syntax_ok"], result["semantic_ok"])
			# Tabs for Tokens, Semantic details, and AST visualization
            tab1, tab2, tab3 = st.tabs(["Lexical", "Semantic", "Visual SDT"])

			# Lexical details in the first tab
            with tab1:
                st.subheader("Tokens")
                st.dataframe(_tokens_as_table(result["tokens"]), width="stretch", hide_index=True)
			
			# Semantic details in the second tab
            with tab2:
                st.subheader("Syntax errors")
                if result["syntax_errors"]:
                    for err in result["syntax_errors"]:
                        st.error(err)
                else:
                    st.success("No syntax errors.")

                st.subheader("Symbol table")
                if result["symbol_table"]:
                    st.dataframe(
                        [{"identifier": k, "type": v} for k, v in result["symbol_table"].items()],
                        width="stretch",
                        hide_index=True,
                    )
                else:
                    st.info("No symbols registered.")

                st.subheader("Semantic errors")
                if result["semantic_errors"]:
                    for err in result["semantic_errors"]:
                        st.error(err)
                elif result["syntax_ok"]:
                    st.success("No semantic errors.")

                st.subheader("SDT trace")
                if result.get("sdt_trace"):
                    st.dataframe(result["sdt_trace"], width="stretch", hide_index=True)
                else:
                    st.info("No SDT trace available.")

			# Visualization of the AST in the third tab
            with tab3:
                st.subheader("AST graph")
                st.caption("Legend:")
                st.caption("Green =  declarations/assignments")
                st.caption("Blue = expressions/operands")
                st.caption("Yellow = control flow (if, while, for)")
                orientation = st.segmented_control(
                    "Orientation",
                    options=["Top-Down", "Bottom-Up"],
                    default="Top-Down",
                )
                rankdir = "TB" if orientation == "Top-Down" else "BT"
                if result["syntax_ok"] and result["ast_dict"]:
                    dot_graph = _ast_to_dot(result["ast_dict"], rankdir=rankdir)
                    st.graphviz_chart(dot_graph)
                else:
                    st.info("Cannot build the graph when syntax errors exist.")

            st.divider()
            
            st.download_button(
                label="Download Analysis Report (JSON)",
                data=json.dumps(
                    {
                        "project": "C-Reload",
                        "syntax_ok": result["syntax_ok"],
                        "syntax_errors": result["syntax_errors"],
                        "semantic_ok": result["semantic_ok"],
                        "semantic_errors": result["semantic_errors"],
                        "symbol_table": result["symbol_table"],
                        "sdt_trace": result.get("sdt_trace", []),
                        "ast": result["ast_dict"],
                        "tokens": _tokens_as_table(result["tokens"]),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                file_name="CReload_report.json",
                mime="application/json",
                use_container_width=True,
            )

if __name__ == "__main__":
	main()