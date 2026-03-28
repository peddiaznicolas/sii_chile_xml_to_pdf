from jinja2 import Environment, PackageLoader, select_autoescape
from weasyprint import HTML, CSS
from num2words import num2words
from typing import Optional, List
from importlib import resources
import io

from .models import DTEData, BHEData
from .formatting import format_clp, fecha_es_larga
from .barcode import pdf417_svg_from_ted
from .parser import parse_xml 
from .bhe_parser import parse_bhe_xml

env = Environment(
    loader=PackageLoader("sii_xml_pdf", "templates"),
    autoescape=select_autoescape(["html"])
)
env.filters["clp"] = format_clp


def _default_css_list(css_path: Optional[str]) -> List[CSS]:
    if css_path:
        return [CSS(filename=css_path)]
    # Cargar el CSS del paquete si no se pasa ruta
    with resources.files("sii_xml_pdf").joinpath("templates/invoice.css").open("r", encoding="utf-8") as f:
        css_text = f.read()
    return [CSS(string=css_text)]


def _bhe_css_list(css_path: Optional[str]) -> List[CSS]:
    if css_path:
        return [CSS(filename=css_path)]
    # Cargar el CSS de BHE del paquete
    with resources.files("sii_xml_pdf").joinpath("templates/bhe.css").open("r", encoding="utf-8") as f:
        css_text = f.read()
    return [CSS(string=css_text)]


def render_html(dte: DTEData) -> str:
    tmpl = env.get_template("invoice.html")
    barcode_svg = pdf417_svg_from_ted(dte.timbre_xml)
    monto_imp_ret = sum(i.monto for i in dte.impuestos) if dte.impuestos else 0
    ctx = {
        "d": dte,
        "fecha_emision_larga": fecha_es_larga(dte.fecha_emision),
        "barcode_svg": barcode_svg,
        "monto_total_palabras": num2words(dte.monto_total, lang="es").upper(),
        "monto_impuesto_y_retenciones": monto_imp_ret,
        "verificacion_url": "http://www.sii.cl",  # visible en el pie
    }
    return tmpl.render(**ctx)


def render_bhe_html(bhe: BHEData) -> str:
    tmpl = env.get_template("bhe.html")
    ctx = {
        "d": bhe,
        "monto_liquido_palabras": num2words(bhe.liquido_honorarios, lang="es").upper(),
    }
    return tmpl.render(**ctx)


def render_pdf(dte: DTEData, css_path: Optional[str] = None) -> bytes:
    html = render_html(dte)
    styles = _default_css_list(css_path)
    out = io.BytesIO()
    HTML(string=html).write_pdf(out, stylesheets=styles)
    return out.getvalue()


def render_bhe_pdf(bhe: BHEData, css_path: Optional[str] = None) -> bytes:
    html = render_bhe_html(bhe)
    styles = _bhe_css_list(css_path)
    out = io.BytesIO()
    HTML(string=html).write_pdf(out, stylesheets=styles)
    return out.getvalue()


def render_pdf_from_xml(xml_bytes: bytes, css_path: Optional[str] = None) -> bytes:
    """
    Recibe XML en bytes, devuelve el PDF en bytes.
    Detecta automáticamente si es DTE o BHE.
    """
    # Intentar detectar el tipo de XML
    xml_str = xml_bytes.decode('utf-8', errors='ignore')
    
    # Si tiene <Documento> y <TED>, es un DTE tradicional
    if '<Documento>' in xml_str and '<TED>' in xml_str:
        dte = parse_xml(xml_bytes)
        return render_pdf(dte, css_path=css_path)
    # Si tiene <datos> y elementos de BHE, es una Boleta de Honorarios
    elif '<datos>' in xml_str or '<rutEmisor>' in xml_str:
        bhe = parse_bhe_xml(xml_bytes)
        return render_bhe_pdf(bhe, css_path=css_path)
    else:
        # Por defecto intentar como DTE
        dte = parse_xml(xml_bytes)
        return render_pdf(dte, css_path=css_path)


def render_bhe_pdf_from_xml(xml_bytes: bytes, translate_to_en: bool = False, css_path: Optional[str] = None) -> bytes:
    """
    Recibe XML de BHE en bytes, devuelve el PDF en bytes.
    
    Args:
        xml_bytes: Contenido del XML en bytes
        translate_to_en: Si True, traduce el contenido al inglés
        css_path: Ruta opcional a archivo CSS personalizado
    """
    bhe = parse_bhe_xml(xml_bytes, translate_to_en=translate_to_en)
    return render_bhe_pdf(bhe, css_path=css_path)
