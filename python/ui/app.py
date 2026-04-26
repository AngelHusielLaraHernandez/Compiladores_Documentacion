# C-Reload: Syntax & Semantic Analyzer (UI)

import logging
import warnings
import os

# ============================================================
# 1. SILENCIADORES DE TERMINAL (DEBEN IR AL PRINCIPIO)
# ============================================================

# Silencia los logs internos de Streamlit (mensajes de "Please replace...")
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Filtros agresivos para advertencias de Python y de Streamlit
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*st\.components\.v1\.html.*")

# ============================================================
# 2. IMPORTACIONES DEL SISTEMA Y STREAMLIT
# ============================================================

import json
import sys

import streamlit as st
import streamlit.components.v1 as components

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


def _inject_theme_detector() -> None:
    """Inject fonts via st.markdown (safe — no script tags needed here)."""
    st.markdown(
        '''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@500;600&family=Montserrat:wght@800;900&family=Playfair+Display:ital,wght@1,700&display=swap" rel="stylesheet">
        ''',
        unsafe_allow_html=True,
    )


def _inject_scripts_component() -> None:
    """Use st.components.v1.html (real iframe) so scripts are GUARANTEED to execute.

    From inside the iframe we access window.parent.document (same-origin, both
    on localhost:8501) to:
      1. Detect Streamlit's theme and set data-cr-theme on the parent <html>.
      2. Force all Streamlit containers to be transparent so the video shows.
      3. Create the #cr-video-bg div with two <video> elements served by GitHub Raw.
      4. Fit Graphviz full-screen frames.
    """
    html_code = f"""<!DOCTYPE html>
<html>
<head><style>html,body{{margin:0;padding:0;background:transparent;}}</style></head>
<body>
<script>
(function() {{
    var pdoc;
    try {{ pdoc = window.parent.document; }} catch(e) {{ return; }}

    // ── Enlaces a GitHub Raw CDN ───────────────────────────────────────────
    var BG_DARK  = 'https://raw.githubusercontent.com/AngelHusielLaraHernandez/Compiladores_Documentacion/main/python/ui/video/darkmode.mp4';
    var BG_LIGHT = 'https://raw.githubusercontent.com/AngelHusielLaraHernandez/Compiladores_Documentacion/main/python/ui/video/lightmode.mp4';

    // ── 1. Theme detection ────────────────────────────────────────────────
    function detectTheme() {{
        var body = pdoc.body;
        if (!body) return;
        var col = window.parent.getComputedStyle(body).color;
        var m = col.match(/\\d+/g);
        if (!m) return;
        var lum = 0.299*+m[0] + 0.587*+m[1] + 0.114*+m[2];
        var theme = lum > 128 ? 'dark' : 'light';
        pdoc.documentElement.setAttribute('data-cr-theme', theme);
    }}

    // ── 2. Force transparency ─────────────────────────────────────────────
    function forceTransparent() {{
        var sels = [
            'html','body','#root','.stApp','.withScreencast',
            '[data-testid="stAppViewContainer"]',
            '[data-testid="stHeader"]',
            '[data-testid="stMain"]',
            '[data-testid="stMainBlockContainer"]',
            'section.main',
            '[data-testid="stFullScreenFrame"]'
        ];
        sels.forEach(function(sel) {{
            pdoc.querySelectorAll(sel).forEach(function(el) {{
                el.style.setProperty('background',       'transparent', 'important');
                el.style.setProperty('background-color', 'transparent', 'important');
            }});
        }});
    }}

    // ── 3. Video background ───────────────────────────────────────────────
    function ensureVideoBg() {{
        if (pdoc.getElementById('cr-video-bg')) return;

        if (!pdoc.getElementById('cr-video-style')) {{
            var style = pdoc.createElement('style');
            style.id = 'cr-video-style';
            style.textContent = [
                '#cr-video-bg{{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none;}}',
                '.cr-bg-video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;',
                '  opacity:0;transition:opacity 1.4s ease;will-change:opacity;}}',
                'html[data-cr-theme="dark"]  #vid-dark  {{opacity:1;}}',
                'html[data-cr-theme="light"] #vid-light {{opacity:1;}}',
                'html:not([data-cr-theme])   #vid-light {{opacity:1;}}'
            ].join('');
            pdoc.head.appendChild(style);
        }}

        var bg = pdoc.createElement('div');
        bg.id = 'cr-video-bg';

        function makeVid(id, src) {{
            var v = pdoc.createElement('video');
            v.id = id;
            v.className = 'cr-bg-video';
            v.autoplay = true;
            v.loop = true;
            v.muted = true;
            v.setAttribute('playsinline', '');
            v.setAttribute('preload', 'auto');
            var s = pdoc.createElement('source');
            s.src  = src;
            s.type = 'video/mp4';
            v.appendChild(s);
            v.load();
            v.play().catch(function(){{}});
            return v;
        }}

        bg.appendChild(makeVid('vid-dark',  BG_DARK));
        bg.appendChild(makeVid('vid-light', BG_LIGHT));
        pdoc.body.insertBefore(bg, pdoc.body.firstChild);
    }}
    
    // ── 4. Fullscreen Detector ────────────────────────────────────────────
    function checkFullscreen() {{
        var isFs = false;
        
        if (pdoc.querySelector('.stFullScreen') || pdoc.querySelector('[data-testid="stFullScreenOverlay"]')) {{
            isFs = true;
        }}

        var vw = window.parent.innerWidth;
        var vh = window.parent.innerHeight;
        pdoc.querySelectorAll('[data-testid="stFullScreenFrame"]').forEach(function(frame) {{
            var rect = frame.getBoundingClientRect();
            if (rect.width > vw * 0.8 && rect.height > vh * 0.8) {{
                isFs = true;
            }}
        }});

        if (isFs) {{
            pdoc.body.setAttribute('data-cr-fullscreen', 'true');
        }} else {{
            pdoc.body.removeAttribute('data-cr-fullscreen');
        }}
    }}

    // ── Bootstrap ─────────────────────────────────────────────────────────
    function bootstrap() {{
        detectTheme();
        forceTransparent();
        ensureVideoBg();
    }}

    bootstrap();
    setInterval(detectTheme,     800);
    setInterval(forceTransparent, 800);
    setInterval(ensureVideoBg,   1500);
    setInterval(checkFullscreen,  300);
    
    try {{
        var obs = new MutationObserver(function() {{
            forceTransparent();
            detectTheme();
            ensureVideoBg();
        }});
        obs.observe(pdoc.body, {{ childList: true, subtree: true }});
    }} catch(e) {{}}
    
}})();
</script>
</body>
</html>"""
    components.html(html_code, height=0, scrolling=False)


def _intro_overlay() -> None:
    """Show a one-time cinematic intro overlay on first page load."""
    if st.session_state.get("intro_shown"):
        return
    st.session_state["intro_shown"] = True

    # Generate particles with varied positions and delays
    particles_html = ""
    import random
    random.seed(42)  # deterministic for consistent experience
    for i in range(20):
        left = random.randint(5, 95)
        top = random.randint(20, 90)
        delay = round(random.uniform(0, 2.5), 2)
        size = random.randint(2, 6)
        opacity = round(random.uniform(0.2, 0.6), 2)
        particles_html += (
            f'<div class="intro-particle" style="'
            f'left:{left}%;top:{top}%;'
            f'width:{size}px;height:{size}px;'
            f'opacity:{opacity};'
            f'animation-delay:{delay}s;'
            f'"></div>'
        )

    st.markdown(
        f'''
        <div class="intro-overlay" id="introOverlay">
            <div class="intro-particles">{particles_html}</div>
            <span class="intro-line-1">Team 1</span>
            <span class="intro-line-2">Compilers</span>
            <span class="intro-line-3">Faculty of Engineering</span>
            <div class="intro-separator"></div>
            <span class="intro-title">C-Reload</span>
            <span class="intro-subtitle">Syntax &amp; Semantic Analyzer</span>
        </div>
        <script>
            setTimeout(function() {{
                var el = document.getElementById('introOverlay');
                if (el) {{ el.classList.add('done'); }}
            }}, 7200);
            setTimeout(function() {{
                var el = document.getElementById('introOverlay');
                if (el) {{ el.remove(); }}
            }}, 7800);
        </script>
        ''',
        unsafe_allow_html=True,
    )

def _background_bubbles() -> None:
    """Inject persistent floating bubbles as animated background."""
    import random
    random.seed(99)
    bubbles = ""
    for _ in range(15):
        left = random.randint(2, 98)
        size = random.randint(18, 70)
        dur = round(random.uniform(12, 28), 1)
        sway = round(random.uniform(4, 8), 1)
        delay = round(random.uniform(0, 14), 1)
        bubbles += (
            f'<div class="bg-bubble" style="'
            f'left:{left}%;'
            f'width:{size}px;height:{size}px;'
            f'--dur:{dur}s;--sway:{sway}s;'
            f'animation-delay:{delay}s,{round(delay/2,1)}s;'
            f'"></div>'
        )
    st.markdown(
        f'<div class="bg-bubbles-container">{bubbles}</div>',
        unsafe_allow_html=True,
    )


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
        return "digraph AST { label=\"AST\"; bgcolor=\"transparent\"; }"

    nodes = []
    edges = []
    count = 0

    def esc(value):
        return str(value).replace('"', '\\"').replace("<", "&lt;").replace(">", "&gt;")

    def node_style(kind):
        if kind in {"if", "if_else", "while", "for", "block"}:
            return "#FFF4CE", "#B08900", "#4A4000"
        if kind in {"declaration", "declaration_list", "assignment", "return"}:
            return "#DFF6DD", "#2E7D32", "#1A4D1E"
        if kind in {"binary_op", "unary_op", "identifier", "constant", "literal"}:
            return "#DDEBFF", "#1E5AA8", "#0E2D54"
        return "#F3F2F1", "#605E5C", "#3B3A39"

    def walk(node, parent_id=None):
        nonlocal count
        count += 1
        node_id = f"n{count}"
        kind = node.get("kind", "node")
        value = node.get("value")
        lineno = node.get("lineno", 0)
        fill, border, font_color = node_style(kind)

        value_text = "-" if value is None else esc(value)
        if len(value_text) > 42:
            value_text = value_text[:39] + "..."
        line_text = f"L{lineno}" if lineno else "-"

        label = (
            "<"
            "<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLPADDING=\"2\">"
            f"<TR><TD><FONT COLOR=\"{font_color}\"><B>{esc(kind)}</B></FONT></TD></TR>"
            f"<TR><TD ALIGN=\"LEFT\"><FONT POINT-SIZE=\"10\" COLOR=\"{font_color}\">value: {value_text}</FONT></TD></TR>"
            f"<TR><TD ALIGN=\"LEFT\"><FONT POINT-SIZE=\"10\" COLOR=\"{font_color}\">line: {line_text}</FONT></TD></TR>"
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
        "bgcolor=\"transparent\";\n"
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
    _inject_theme_detector()        # fonts only (safe st.markdown)
    _inject_scripts_component()     # iframe → scripts guaranteed to run
    _load_css()
    _intro_overlay()
    _background_bubbles()

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

    # Titles and Beta Toggle
    col_title, col_toggle = st.columns([3, 1], vertical_alignment="bottom")
    with col_title:
        st.markdown('<div class="project-title">C-Reload</div>', unsafe_allow_html=True)
        st.markdown("#### Syntax & Semantic Analyzer")
    with col_toggle:
        beta_mode = st.toggle("Modo Beta (Estatico)")

    # Si el Modo Beta está activo, inyectamos CSS para sobreescribir el diseño
    if beta_mode:
        st.markdown("""
        <style>
            /* 1. Ocultar los videos dinámicos */
            #cr-video-bg { display: none !important; }
            
            /* 2. Fondo estático radial de la presentación */
            .stApp, [data-testid="stAppViewContainer"] {
                background: radial-gradient(ellipse at center, #0f1628 0%, #060a14 70%, #000000 100%) !important;
            }

            /* 3. Adaptación del Modo Luz (Persona 3) para fondo oscuro */
            /* Forzar textos principales a blanco para legibilidad */
            .stApp * {
                color: #ffffff !important;
            }
            
            /* Mantener el color Cyan vibrante como acento en títulos */
            h1, h2, h3, h4, .status-title {
                text-transform: uppercase !important;
                font-style: italic !important;
                font-weight: 900 !important;
                text-shadow: 2px 2px 0px #00BFFF !important;
            }

            /* Contenedores con bordes afilados (estilo modo luz) */
            .status-card, [data-testid="stMetric"], div[data-baseweb="select"] > div, textarea {
                background-color: rgba(30, 33, 44, 0.8) !important;
                border: 2px solid #00BFFF !important;
                border-radius: 0px !important; /* Esquinas afiladas */
            }

            /* Botón analizar agresivo e inclinado */
            .stButton > button {
                border-radius: 0px !important;
                border: 3px solid #00BFFF !important;
                background: rgba(0, 0, 0, 0.5) !important;
                color: #00BFFF !important;
                font-weight: 900 !important;
                font-style: italic !important;
                text-transform: uppercase !important;
                box-shadow: 4px 4px 0px rgba(0, 191, 255, 0.4) !important;
            }
            .stButton > button:hover {
                background-color: #00BFFF !important;
                color: #000000 !important;
                box-shadow: none !important;
                transform: translate(2px, 2px);
            }
            
            /* Tabs estilo P3 */
            .stTabs [data-baseweb="tab"] {
                border-radius: 0px !important;
                border: 2px solid transparent !important;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                border: 2px solid #00BFFF !important;
                background-color: rgba(0, 191, 255, 0.2) !important;
            }
            
            /* Corregir flecha del selector */
            [data-testid="stSelectbox"] svg {
                fill: #00BFFF !important;
            }
        </style>
        """, unsafe_allow_html=True)

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
            uploaded = st.file_uploader("Upload C code", type=["c", "txt"], label_visibility="collapsed")
            
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
            if st.button("Analyze", type="primary", width="stretch"):
                with st.spinner("Analyzing..."):
                    st.session_state["analysis_result"] = parse_source(st.session_state["source_code"])


    with output_col:
        st.subheader("Output")
        result = st.session_state.get("analysis_result")
        if result is None:
            st.info("Select or edit a sample on the left, then click **Analyze**.")
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
                st.markdown(
                    '''
                    <div class="legend-row">
                        <span class="legend-badge green"><span class="legend-dot green"></span>Declarations / Assignments</span>
                        <span class="legend-badge blue"><span class="legend-dot blue"></span>Expressions / Operands</span>
                        <span class="legend-badge yellow"><span class="legend-dot yellow"></span>Control flow (if, while, for)</span>
                        <span class="legend-badge gray"><span class="legend-dot gray"></span>Other nodes</span>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
                orientation = st.segmented_control(
                    "Orientation",
                    options=["Top-Down", "Bottom-Up"],
                    default="Top-Down",
                )
                rankdir = "TB" if orientation == "Top-Down" else "BT"
                
                if result["syntax_ok"] and result["ast_dict"]:
                    dot_graph = _ast_to_dot(result["ast_dict"], rankdir=rankdir)
                    st.graphviz_chart(dot_graph, width="stretch")
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
                width="stretch",
            )

if __name__ == "__main__":
    main()