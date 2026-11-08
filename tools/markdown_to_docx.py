#!/usr/bin/env python3
"""
markdown_to_docx.py - Generador de Informe Final Académico en Word (.docx)
Convierte Informe_Final_Integrado_v4.md en un documento Microsoft Word (.docx)
listo para entregar según las pautas de Trabajo_Final_IO2_2026.md (UCASAL - IO2).

Características:
- Hoja A4 con márgenes de 2,5 cm, encabezado institucional y numeración de páginas en el pie.
- Portada dedicada en Página 1 con Logo UCASAL centrado, datos de cátedra e integrantes.
- Ecuaciones en bloque ($$...$$) convertidas a ecuaciones nativas editables de Word (OMML <m:oMathPara>).
- Expresiones matemáticas en línea ($...$) convertidas a tipografía nativa con símbolos Unicode,
  cursivas, subíndices y superíndices reales (sin dejar código LaTeX crudo).
- Tablas académicas con encabezado sombreado (#D9E2F3), repetición de cabecera (tblHeader),
  protección de corte de fila (cantSplit) y alineación automática por columna.
- Figuras en alta resolución (300 DPI) centradas con su epígrafe debajo.
"""

import os
import re
import sys
import pathlib
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

# Mapa completo de comandos LaTeX a símbolos Unicode
LATEX_SYMBOLS = {
    r"\lambda": "λ",
    r"\mu": "μ",
    r"\rho": "ρ",
    r"\tau": "τ",
    r"\sigma": "σ",
    r"\alpha": "α",
    r"\beta": "β",
    r"\theta": "θ",
    r"\pi": "π",
    r"\Delta": "Δ",
    r"\pm": "±",
    r"\le": "≤",
    r"\leq": "≤",
    r"\ge": "≥",
    r"\geq": "≥",
    r"\ne": "≠",
    r"\neq": "≠",
    r"\approx": "≈",
    r"\times": "×",
    r"\cdot": "·",
    r"\to": "→",
    r"\rightarrow": "→",
    r"\infty": "∞",
    r"\in": "∈",
    r"\cap": "∩",
    r"\cup": "∪",
    r"\emptyset": "∅",
    r"\sum": "∑",
    r"\int": "∫",
    r"\quad": "   ",
    r"\qquad": "     ",
    r"\,": " ",
    r"\;": " ",
    r"\:": " ",
    r"\!": "",
    r"\%": "%",
    r"\{": "{",
    r"\}": "}",
}


def set_cell_background(cell, fill_hex: str):
    """Aplica color de fondo hexadecimal a una celda de tabla."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, left=110, right=110):
    """Configura márgenes internos compactos en dxa (1/20 de punto)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for side, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="BFBFBF", sz="4"):
    """Define bordes limpios para toda la tabla."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'  <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'  <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="E2E8F0"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def mark_row_header_and_cant_split(row, is_header=False):
    """Evita que la fila se parta entre páginas y repite encabezado si corresponde."""
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))
    if is_header:
        trPr.append(OxmlElement("w:tblHeader"))


def add_page_number_to_run(run):
    """Inserta campo PAGE dinámico de Word en un run del pie de página."""
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls("w"))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls("w"))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


# ==============================================================================
# PARSER DE ECUACIONES LATEX A OMML NATIVO DE WORD (<m:oMathPara> y <m:oMath>)
# ==============================================================================

def extract_braced(s: str, pos: int):
    """Extrae el contenido entre llaves { ... } balanceadas comenzando en pos."""
    if pos >= len(s) or s[pos] != "{":
        return None, pos
    depth = 0
    i = pos
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            i += 2
            continue
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[pos + 1 : i], i + 1
        i += 1
    return s[pos + 1 :], len(s)


def make_m_run(text: str, normal: bool = False):
    """Crea un elemento <m:r> de OMML."""
    r = etree.Element(f"{{{M_NS}}}r")
    if normal:
        rPr = etree.SubElement(r, f"{{{M_NS}}}rPr")
        etree.SubElement(rPr, f"{{{M_NS}}}nor")
    w_rPr = etree.SubElement(r, f"{{{W_NS}}}rPr")
    rFonts = etree.SubElement(w_rPr, f"{{{W_NS}}}rFonts")
    rFonts.set(f"{{{W_NS}}}ascii", "Cambria Math")
    rFonts.set(f"{{{W_NS}}}hAnsi", "Cambria Math")
    t = etree.SubElement(r, f"{{{M_NS}}}t")
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def parse_SingleAtom_omml(s: str, pos: int):
    """Lee un único átomo LaTeX para subíndice/superíndice o base."""
    while pos < len(s) and s[pos] in " \t":
        pos += 1
    if pos >= len(s):
        return [make_m_run("")], pos
    if s[pos] == "{":
        content, next_pos = extract_braced(s, pos)
        return latex_to_omml_nodes(content), next_pos
    if s[pos] == "\\":
        m = re.match(r"\\[a-zA-Z]+|\\.", s[pos:])
        if m:
            cmd = m.group(0)
            next_pos = pos + len(cmd)
            if cmd == r"\text":
                content, next_pos = extract_braced(s, next_pos)
                cleaned = replace_simple_latex_symbols(content or "")
                return [make_m_run(cleaned, normal=True)], next_pos
            if cmd in LATEX_SYMBOLS:
                return [make_m_run(LATEX_SYMBOLS[cmd])], next_pos
            return [make_m_run(cmd.lstrip("\\"), normal=True)], next_pos
    return [make_m_run(s[pos])], pos + 1


def replace_simple_latex_symbols(text: str) -> str:
    """Reemplaza comandos LaTeX simples por su equivalente Unicode."""
    res = text
    # Primero comandos largos para evitar colisiones de prefijos (\leq antes de \le)
    for k in sorted(LATEX_SYMBOLS.keys(), key=len, reverse=True):
        res = res.replace(k, LATEX_SYMBOLS[k])
    return res


def attach_sub_sup(base_nodes, sub_nodes, sup_nodes):
    """Construye <m:sSub>, <m:sSup> o <m:sSubSup> en OMML."""
    if sub_nodes is not None and sup_nodes is not None:
        el = etree.Element(f"{{{M_NS}}}sSubSup")
        e_node = etree.SubElement(el, f"{{{M_NS}}}e")
        for n in base_nodes:
            e_node.append(n)
        sub_el = etree.SubElement(el, f"{{{M_NS}}}sub")
        for n in sub_nodes:
            sub_el.append(n)
        sup_el = etree.SubElement(el, f"{{{M_NS}}}sup")
        for n in sup_nodes:
            sup_el.append(n)
        return el
    elif sub_nodes is not None:
        el = etree.Element(f"{{{M_NS}}}sSub")
        e_node = etree.SubElement(el, f"{{{M_NS}}}e")
        for n in base_nodes:
            e_node.append(n)
        sub_el = etree.SubElement(el, f"{{{M_NS}}}sub")
        for n in sub_nodes:
            sub_el.append(n)
        return el
    elif sup_nodes is not None:
        el = etree.Element(f"{{{M_NS}}}sSup")
        e_node = etree.SubElement(el, f"{{{M_NS}}}e")
        for n in base_nodes:
            e_node.append(n)
        sup_el = etree.SubElement(el, f"{{{M_NS}}}sup")
        for n in sup_nodes:
            sup_el.append(n)
        return el
    return base_nodes[0] if len(base_nodes) == 1 else base_nodes


def latex_to_omml_nodes(s: str):
    """Convierte una cadena LaTeX en una lista de nodos XML OMML."""
    nodes = []
    s = s.strip()
    s = s.replace(r"\left", "").replace(r"\right", "")
    pos = 0
    while pos < len(s):
        ch = s[pos]
        if ch in " \t\n":
            pos += 1
            continue

        base_nodes = None
        if ch == "{":
            content, pos = extract_braced(s, pos)
            base_nodes = latex_to_omml_nodes(content or "")
        elif ch == "\\":
            m = re.match(r"\\[a-zA-Z]+|\\.", s[pos:])
            cmd = m.group(0) if m else "\\"
            pos += len(cmd)

            if cmd == r"\frac" or cmd == r"\tfrac":
                num_str, pos = extract_braced(s, pos)
                while pos < len(s) and s[pos] == " ":
                    pos += 1
                den_str, pos = extract_braced(s, pos)
                f_el = etree.Element(f"{{{M_NS}}}f")
                num_el = etree.SubElement(f_el, f"{{{M_NS}}}num")
                for n in latex_to_omml_nodes(num_str or ""):
                    num_el.append(n)
                den_el = etree.SubElement(f_el, f"{{{M_NS}}}den")
                for n in latex_to_omml_nodes(den_str or ""):
                    den_el.append(n)
                base_nodes = [f_el]
            elif cmd == r"\sqrt":
                rad_str, pos = extract_braced(s, pos)
                rad_el = etree.Element(f"{{{M_NS}}}rad")
                radPr = etree.SubElement(rad_el, f"{{{M_NS}}}radPr")
                degHide = etree.SubElement(radPr, f"{{{M_NS}}}degHide")
                degHide.set(f"{{{M_NS}}}val", "1")
                etree.SubElement(rad_el, f"{{{M_NS}}}deg")
                e_el = etree.SubElement(rad_el, f"{{{M_NS}}}e")
                for n in latex_to_omml_nodes(rad_str or ""):
                    e_el.append(n)
                base_nodes = [rad_el]
            elif cmd in (r"\bar", r"\hat"):
                acc_str, pos = extract_braced(s, pos)
                acc_el = etree.Element(f"{{{M_NS}}}acc")
                accPr = etree.SubElement(acc_el, f"{{{M_NS}}}accPr")
                chr_el = etree.SubElement(accPr, f"{{{M_NS}}}chr")
                chr_el.set(f"{{{M_NS}}}val", "\u0305" if cmd == r"\bar" else "\u0302")
                e_el = etree.SubElement(acc_el, f"{{{M_NS}}}e")
                for n in latex_to_omml_nodes(acc_str or ""):
                    e_el.append(n)
                base_nodes = [acc_el]
            elif cmd == r"\text":
                txt_str, pos = extract_braced(s, pos)
                cleaned = replace_simple_latex_symbols(txt_str or "")
                base_nodes = [make_m_run(cleaned, normal=True)]
            elif cmd in (r"\min", r"\max", r"\ln", r"\exp"):
                base_nodes = [make_m_run(cmd.lstrip("\\"), normal=True)]
            elif cmd in LATEX_SYMBOLS:
                sym = LATEX_SYMBOLS[cmd]
                if sym == "":
                    continue
                base_nodes = [make_m_run(sym, normal=(cmd in (r"\quad", r"\qquad", r"\,", r"\;")))]
            else:
                base_nodes = [make_m_run(cmd.lstrip("\\"), normal=True)]
        else:
            # Agrupar dígitos/comas decimales consecutivos o signos normales
            if ch.isdigit():
                m_num = re.match(r"[0-9]+(?:,[0-9]+)?", s[pos:])
                num_txt = m_num.group(0)
                pos += len(num_txt)
                base_nodes = [make_m_run(num_txt, normal=True)]
            elif ch in "+-=()[]|;:,.<>!/":
                pos += 1
                txt = f" {ch} " if ch in "+-=" else ch
                base_nodes = [make_m_run(txt, normal=True)]
            else:
                pos += 1
                base_nodes = [make_m_run(ch, normal=False)]

        # Verificar si siguen subíndices (_) o superíndices (^)
        sub_nodes = None
        sup_nodes = None
        for _ in range(2):
            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos < len(s) and s[pos] == "_":
                sub_nodes, pos = parse_SingleAtom_omml(s, pos + 1)
            elif pos < len(s) and s[pos] == "^":
                sup_nodes, pos = parse_SingleAtom_omml(s, pos + 1)

        if sub_nodes is not None or sup_nodes is not None:
            nodes.append(attach_sub_sup(base_nodes, sub_nodes, sup_nodes))
        else:
            nodes.extend(base_nodes)

    return nodes


def add_display_equation(doc, latex_expr: str):
    """Agrega un párrafo con ecuación nativa centrada de Word (<m:oMathPara>)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)

    oMathPara = etree.Element(f"{{{M_NS}}}oMathPara")
    oMath = etree.SubElement(oMathPara, f"{{{M_NS}}}oMath")
    for n in latex_to_omml_nodes(latex_expr):
        oMath.append(n)
    p._p.append(oMathPara)
    return p


def append_inline_omml(paragraph, latex_expr: str):
    """Inserta una ecuación <m:oMath> en línea dentro de un párrafo existente."""
    oMath = etree.Element(f"{{{M_NS}}}oMath")
    for n in latex_to_omml_nodes(latex_expr):
        oMath.append(n)
    paragraph._p.append(oMath)


# ==============================================================================
# FORMATEADOR DE TEXTO EN LÍNEA Y EXPRESIONES MATEMÁTICAS ($...$)
# ==============================================================================

def render_inline_math_to_runs(paragraph, math_str: str, base_bold=False, font_size=None):
    r"""
    Convierte una expresión matemática en línea $...$ en runs nativos de Word
    con cursivas, subíndices, superíndices y símbolos griegos/matemáticos reales.
    Si contiene \frac o \sqrt, inserta directamente un nodo <m:oMath> en línea.
    """
    s = math_str.strip()
    if r"\frac" in s or r"\tfrac" in s or r"\sqrt" in s or r"\sum_" in s or r"\int_" in s:
        append_inline_omml(paragraph, s)
        return

    # Pre-limpieza de acentos comunes en línea: \bar{X}, \hat{S}, |\bar{K}_i|
    s = re.sub(r"\\bar\{([a-zA-Z0-9]+)\}", lambda m: m.group(1) + "\u0304", s)
    s = re.sub(r"\\hat\{([a-zA-Z0-9]+)\}", lambda m: m.group(1) + "\u0302", s)
    s = s.replace(r"\left", "").replace(r"\right", "")

    pos = 0
    while pos < len(s):
        if s[pos] == "\\":
            m = re.match(r"\\[a-zA-Z]+|\\.", s[pos:])
            cmd = m.group(0) if m else "\\"
            pos += len(cmd)
            if cmd == r"\text":
                txt, pos = extract_braced(s, pos)
                run = paragraph.add_run(replace_simple_latex_symbols(txt or ""))
                run.bold = base_bold
                if font_size:
                    run.font.size = font_size
            elif cmd in LATEX_SYMBOLS:
                sym = LATEX_SYMBOLS[cmd]
                if sym:
                    run = paragraph.add_run(sym)
                    run.bold = base_bold
                    if font_size:
                        run.font.size = font_size
            else:
                run = paragraph.add_run(cmd.lstrip("\\"))
                run.bold = base_bold
                if font_size:
                    run.font.size = font_size
        elif s[pos] in ("_", "^"):
            mode = s[pos]
            pos += 1
            if pos < len(s) and s[pos] == "{":
                sub_txt, pos = extract_braced(s, pos)
            elif pos < len(s) and s[pos] == "\\":
                m = re.match(r"\\[a-zA-Z]+|\\.", s[pos:])
                sub_txt = m.group(0)
                pos += len(sub_txt)
            elif pos < len(s):
                sub_txt = s[pos]
                pos += 1
            else:
                sub_txt = ""
            # Limpiar \text{...} dentro del subíndice
            sub_txt = re.sub(r"\\text\{([^}]*)\}", r"\1", sub_txt or "")
            sub_txt = replace_simple_latex_symbols(sub_txt)
            run = paragraph.add_run(sub_txt)
            run.bold = base_bold
            if mode == "_":
                run.font.subscript = True
            else:
                run.font.superscript = True
            if font_size:
                run.font.size = font_size
        elif s[pos] == "{":
            inner, pos = extract_braced(s, pos)
            render_inline_math_to_runs(paragraph, inner or "", base_bold=base_bold, font_size=font_size)
        else:
            # Leer secuencia de caracteres normales
            m_plain = re.match(r"[^\\_{}^]+", s[pos:])
            chunk = m_plain.group(0)
            pos += len(chunk)
            # Separar letras (variables en cursiva si son identificadores matemáticos) de números/símbolos
            for tok in re.findall(r"[A-Za-z\u0300-\u036f]+|[^A-Za-z\u0300-\u036f]+", chunk):
                # Espaciar operadores =, +, <, > cuando no son parte de intervalo negativo
                run = paragraph.add_run(tok)
                run.bold = base_bold
                if tok.isalpha() and tok not in ("min", "max", "ln", "exp", "h", "pp", "doc", "gl", "IC"):
                    run.italic = True
                if font_size:
                    run.font.size = font_size


def add_formatted_text(paragraph, text: str, font_size=None, default_italic=False, default_bold=False):
    """
    Parsea negritas (**...**), cursivas (*...*), código (`...`), enlaces [txt](url)
    y matemática en línea ($...$) agregando runs al párrafo.
    """
    # Convertir enlaces markdown [texto](url) -> texto (excepto si el texto ya es la URL)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)

    # Tokenizar por **...**, *...*, `...` y $...$ (permitiendo *cursiva* anidada dentro de **negrita**)
    token_pattern = re.compile(
        r"(\*\*(?:(?!\*\*).)+\*\*|\$[^$]+\$|`[^`]+`|\*[^*\s][^*]*?\*)"
    )

    pos = 0
    for m in token_pattern.finditer(text):
        if m.start() > pos:
            plain = text[pos : m.start()]
            r = paragraph.add_run(plain)
            r.bold = default_bold
            r.italic = default_italic
            if font_size:
                r.font.size = font_size

        tok = m.group(0)
        if tok.startswith("**") and tok.endswith("**"):
            inner = tok[2:-2]
            add_formatted_text(paragraph, inner, font_size=font_size, default_italic=default_italic, default_bold=True)
        elif tok.startswith("$") and tok.endswith("$"):
            inner = tok[1:-1]
            render_inline_math_to_runs(paragraph, inner, base_bold=default_bold, font_size=font_size)
        elif tok.startswith("`") and tok.endswith("`"):
            inner = tok[1:-1]
            r = paragraph.add_run(inner)
            r.font.name = "Consolas"
            r.bold = default_bold
            r.font.size = Pt(font_size.pt - 0.5) if font_size else Pt(9.5)
        elif tok.startswith("*") and tok.endswith("*"):
            inner = tok[1:-1]
            add_formatted_text(paragraph, inner, font_size=font_size, default_italic=True, default_bold=default_bold)

        pos = m.end()

    if pos < len(text):
        r = paragraph.add_run(text[pos:])
        r.bold = default_bold
        r.italic = default_italic
        if font_size:
            r.font.size = font_size


# ==============================================================================
# CONSTRUCCIÓN DEL DOCUMENTO WORD COMPLETO
# ==============================================================================

def configure_styles_and_page(doc: Document):
    """Configura hoja A4, márgenes académicos compactos, estilos de títulos y pie de página."""
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)
    section.different_first_page_header_footer = True

    # Encabezado en páginas interiores
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("Investigación Operativa II — Trabajo Final Integrador (2026)")
    hrun.font.name = "Calibri"
    hrun.font.size = Pt(8.5)
    hrun.font.color.rgb = RGBColor(100, 116, 139)

    # Pie de página con número de página
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun1 = fp.add_run("Página ")
    frun1.font.name = "Calibri"
    frun1.font.size = Pt(9)
    frun1.font.color.rgb = RGBColor(100, 116, 139)
    frun_pg = fp.add_run()
    frun_pg.font.name = "Calibri"
    frun_pg.font.size = Pt(9)
    frun_pg.font.color.rgb = RGBColor(100, 116, 139)
    add_page_number_to_run(frun_pg)

    # Estilo Normal
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(15, 23, 42)
    normal.paragraph_format.line_spacing = 1.08
    normal.paragraph_format.space_after = Pt(3)

    # Estilos Heading 1, 2, 3
    heading_specs = [
        ("Heading 1", 13, RGBColor(15, 35, 75), 9, 3),
        ("Heading 2", 11, RGBColor(25, 55, 109), 6, 2),
        ("Heading 3", 10, RGBColor(40, 75, 130), 4, 1.5),
    ]
    for name, pt_size, color, sp_before, sp_after in heading_specs:
        st = doc.styles[name]
        st.font.name = "Calibri"
        st.font.size = Pt(pt_size)
        st.font.bold = True
        st.font.color.rgb = color
        st.paragraph_format.space_before = Pt(sp_before)
        st.paragraph_format.space_after = Pt(sp_after)
        st.paragraph_format.keep_with_next = True


def build_cover_page(doc: Document, base_dir: pathlib.Path):
    """Construye la portada institucional en la Página 1."""
    logo_path = base_dir / "graficos" / "Logo-UCASAL.jpg"
    if logo_path.exists():
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(12)
        p_logo.paragraph_format.space_after = Pt(10)
        run_logo = p_logo.add_run()
        run_logo.add_picture(str(logo_path), width=Cm(5.2))

    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_after = Pt(2)
    r_uni = p_uni.add_run("UNIVERSIDAD CATÓLICA DE SALTA")
    r_uni.font.size = Pt(16)
    r_uni.font.bold = True
    r_uni.font.color.rgb = RGBColor(15, 35, 75)

    p_fac = doc.add_paragraph()
    p_fac.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fac.paragraph_format.space_after = Pt(28)
    r_fac = p_fac.add_run("Facultad de Ingeniería · Ingeniería en Informática")
    r_fac.font.size = Pt(12.5)
    r_fac.font.bold = True
    r_fac.font.color.rgb = RGBColor(71, 85, 105)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(18)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run(
        "Sistema de turnos dinámicos con recomendación de vacantes para las asambleas de designación docente en Salta"
    )
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(36)
    r_sub = p_sub.add_run("Trabajo Final Integrador — Modalidad A (Aplicación Práctica)")
    r_sub.font.size = Pt(12.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(51, 65, 85)

    meta_rows = [
        ("Carrera:", "Ingeniería en Informática"),
        ("Asignatura:", "Investigación Operativa II"),
        ("Profesor Titular:", "Mg. Ing. Gustavo Ramiro Rivadera"),
        ("Profesor Auxiliar:", "Ing. Gustavo Flores Vargas"),
        ("Integrantes:", "Emiliano Javier Aguirre — DNI 45.770.631\nPablo Celaya — DNI 45.115.839"),
        ("Año:", "2026"),
    ]
    tbl = doc.add_table(rows=len(meta_rows), cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="CBD5E1", sz="4")
    for idx, (label, val) in enumerate(meta_rows):
        row = tbl.rows[idx]
        mark_row_header_and_cant_split(row, is_header=False)
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Cm(4.8)
        c1.width = Cm(9.5)
        set_cell_margins(c0, top=100, bottom=100, left=140, right=140)
        set_cell_margins(c1, top=100, bottom=100, left=140, right=140)
        set_cell_background(c0, "F1F5F9")
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(10.5)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.size = Pt(10.5)

    doc.add_page_break()


def render_markdown_table(doc: Document, table_lines: list):
    """Convierte un bloque de tabla Markdown en una tabla Word estilizada."""
    rows_raw = []
    alignments = []
    for idx, line in enumerate(table_lines):
        stripped = line.strip().strip("|")
        cells = [c.strip() for c in stripped.split("|")]
        if idx == 1 and all(re.match(r"^:?-{2,}:?$", c) for c in cells):
            for c in cells:
                if c.startswith(":") and c.endswith(":"):
                    alignments.append(WD_ALIGN_PARAGRAPH.CENTER)
                elif c.endswith(":"):
                    alignments.append(WD_ALIGN_PARAGRAPH.RIGHT)
                else:
                    alignments.append(WD_ALIGN_PARAGRAPH.LEFT)
            continue
        rows_raw.append(cells)

    if not rows_raw:
        return

    num_cols = max(len(r) for r in rows_raw)
    if not alignments:
        alignments = [WD_ALIGN_PARAGRAPH.LEFT] + [WD_ALIGN_PARAGRAPH.CENTER] * (num_cols - 1)

    tbl = doc.add_table(rows=len(rows_raw), cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = True
    set_table_borders(tbl, color="CBD5E1", sz="4")

    # Calcular anchos proporcionales de columna según el contenido para evitar quiebres de línea excesivos
    total_width_cm = 16.6
    col_weights = []
    for c_idx in range(num_cols):
        max_len = max((len(re.sub(r"[$*`\\]", "", r[c_idx])) for r in rows_raw if c_idx < len(r)), default=8)
        # Raíz cuadrada suaviza diferencias extremas pero da más ancho a columnas descriptivas
        w = max(1.3, min(7.0, (max_len ** 0.58) * 0.65))
        if c_idx == 0 and num_cols >= 3:
            w = max(w, 3.8)
        col_weights.append(w)
    sum_w = sum(col_weights)
    col_widths_cm = [total_width_cm * (w / sum_w) for w in col_weights]

    # Ajustar fuente según cantidad de columnas para que quepa cómodo en A4
    cell_font_pt = Pt(8.0) if num_cols >= 6 else Pt(8.8)

    for r_idx, row_cells in enumerate(rows_raw):
        row = tbl.rows[r_idx]
        is_hdr = r_idx == 0
        mark_row_header_and_cant_split(row, is_header=is_hdr)
        for c_idx in range(num_cols):
            cell_text = row_cells[c_idx] if c_idx < len(row_cells) else ""
            cell = row.cells[c_idx]
            cell.width = Cm(col_widths_cm[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=32, bottom=32, left=55, right=55)
            if is_hdr:
                set_cell_background(cell, "D9E2F3")
            elif r_idx % 2 == 0:
                set_cell_background(cell, "F8FAFC")

            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.02
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_hdr else (
                alignments[c_idx] if c_idx < len(alignments) else WD_ALIGN_PARAGRAPH.LEFT
            )
            add_formatted_text(p, cell_text, font_size=cell_font_pt, default_bold=is_hdr)


def convert_markdown_to_docx(md_path: pathlib.Path, docx_path: pathlib.Path):
    """Lee el archivo Markdown y genera el documento Word completo."""
    doc = Document()
    base_dir = md_path.parent
    configure_styles_and_page(doc)
    build_cover_page(doc, base_dir)

    lines = md_path.read_text(encoding="utf-8").splitlines()

    # Saltar el bloque de portada en el Markdown hasta llegar a "## ÍNDICE"
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("## ÍNDICE"):
            start_idx = i
            break

    i = start_idx
    in_references = False
    in_toc = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped or stripped == "---":
            i += 1
            continue

        # Ecuación en bloque $$ ... $$
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            eq_str = stripped[2:-2].strip()
            add_display_equation(doc, eq_str)
            i += 1
            continue

        # Imagen ![caption](path)
        m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if m_img:
            caption, rel_path = m_img.group(1), m_img.group(2)
            img_file = base_dir / rel_path
            if img_file.exists():
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(4)
                p_img.paragraph_format.space_after = Pt(1)
                p_img.paragraph_format.keep_with_next = True
                run_img = p_img.add_run()
                run_img.add_picture(str(img_file), width=Cm(12.2))

                if caption:
                    p_cap = doc.add_paragraph()
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_cap.paragraph_format.space_before = Pt(0)
                    p_cap.paragraph_format.space_after = Pt(4)
                    add_formatted_text(p_cap, caption, font_size=Pt(8.5), default_italic=True)
            i += 1
            continue

        # Tabla Markdown
        if stripped.startswith("|") and stripped.endswith("|"):
            table_block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_block.append(lines[i])
                i += 1
            render_markdown_table(doc, table_block)
            continue

        # Encabezados ##, ###, ####
        if stripped.startswith("## "):
            title_txt = stripped[3:].strip()
            in_toc = title_txt.upper() == "ÍNDICE"
            in_references = "REFERENCIAS BIBLIOGRÁFICAS" in title_txt.upper()
            h = doc.add_heading(level=1)
            add_formatted_text(h, title_txt, font_size=Pt(12.5), default_bold=True)
            i += 1
            continue
        elif stripped.startswith("### "):
            title_txt = stripped[4:].strip()
            h = doc.add_heading(level=2)
            add_formatted_text(h, title_txt, font_size=Pt(11), default_bold=True)
            i += 1
            continue
        elif stripped.startswith("#### "):
            title_txt = stripped[5:].strip()
            h = doc.add_heading(level=3)
            add_formatted_text(h, title_txt, font_size=Pt(10), default_bold=True)
            i += 1
            continue

        # Listas con viñetas o numeradas
        m_list = re.match(r"^(\s*)([*\-]|\d+\.)\s+(.*)$", line)
        if m_list:
            indent_spaces = len(m_list.group(1))
            marker = m_list.group(2)
            item_text = m_list.group(3).strip()

            p = doc.add_paragraph()
            if in_toc:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 0.95
                left_cm = 0.2 if indent_spaces == 0 else 0.7
                p.paragraph_format.left_indent = Cm(left_cm)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                add_formatted_text(p, item_text, font_size=Pt(8.5), default_bold=(indent_spaces == 0))
            elif in_references:
                # Sangría francesa estilo APA para la bibliografía
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05
                p.paragraph_format.left_indent = Cm(0.8)
                p.paragraph_format.first_line_indent = Cm(-0.8)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                add_formatted_text(p, item_text, font_size=Pt(9.0))
            else:
                p.paragraph_format.space_before = Pt(0.5)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.08
                left_cm = 0.5 if indent_spaces == 0 else 1.0
                p.paragraph_format.left_indent = Cm(left_cm)
                p.paragraph_format.first_line_indent = Cm(-0.35)
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                prefix = f"{marker} " if marker[0].isdigit() else ("• " if indent_spaces == 0 else "◦ ")
                r_pre = p.add_run(prefix)
                r_pre.bold = marker[0].isdigit()
                add_formatted_text(p, item_text, font_size=Pt(10))
            i += 1
            continue

        # Párrafo normal
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.08
        add_formatted_text(p, stripped, font_size=Pt(10))
        i += 1

    doc.save(str(docx_path))
    print(f"Documento Word generado exitosamente en: {docx_path}")


if __name__ == "__main__":
    md_in = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("Informe_Final_Integrado_v4.md")
    docx_out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path("Informe_Final_Integrado_v4.docx")
    convert_markdown_to_docx(md_in, docx_out)
