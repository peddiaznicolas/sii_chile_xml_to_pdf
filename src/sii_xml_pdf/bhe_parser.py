"""Parser para Boleta de Honorarios Electrónica (BHE)"""
import xml.etree.ElementTree as ET
from typing import Union, List
from pathlib import Path
from .models import BHEData, BHEItem

# Diccionario de traducciones español -> inglés
TRANSLATIONS = {
    "Boleta de Honorarios Electrónica": "Electronic Fee Receipt",
    "Boleta de Honorarios": "Fee Receipt",
    "RUT Emisor": "Issuer RUT",
    "RUT Receptor": "Recipient RUT",
    "Nombre": "Name",
    "Giro": "Business Activity",
    "Actividad Económica": "Economic Activity",
    "Actividad Economica": "Economic Activity",
    "Domicilio": "Address",
    "Comuna": "Commune",
    "Teléfono": "Phone",
    "Telefono": "Phone",
    "Fecha": "Date",
    "Número": "Number",
    "Líquido a Pagar": "Net to Pay",
    "Liquido a Pagar": "Net to Pay",
    "Impuesto": "Tax",
    "Total Honorarios": "Total Fees",
    "Retiene Emisor": "Withheld by Issuer",
    "Sí": "Yes",
    "No": "No",
    "Descripción": "Description",
    "Descripcion": "Description",
    "Valor Servicio": "Service Value",
    "Servicios Profesionales": "Professional Services",
    "Código Alfa": "Alpha Code",
    "Codigo Alfa": "Alpha Code",
    "Generación": "Generation",
    "Generacion": "Generation",
    "Envío": "Sending",
    "Envio": "Sending",
    "SERVICIOS": "SERVICES",
    "OPTIMIZACION": "OPTIMIZATION",
    "EN": "IN",
    "ERP": "ERP",
    "Y": "AND",
    "CONSULTOR": "CONSULTANT",
    "DE": "OF",
    "INFORMATICA": "IT",
}


def _text(el, default=""):
    """Obtiene el texto de un elemento XML"""
    if el is None:
        return default
    return (el.text or default).strip()


def _int_text(el, default=0):
    """Obtiene un entero de un elemento XML"""
    try:
        t = _text(el)
        return int(t) if t else default
    except Exception:
        return default


def _format_rut(rut: str, dv: str) -> str:
    """Formatea un RUT chileno a la forma 12.345.678-9"""
    if not rut:
        return ""
    
    rut = rut.strip().replace(".", "").replace("-", "")
    cuerpo_formateado = ""
    
    while len(rut) > 3:
        cuerpo_formateado = "." + rut[-3:] + cuerpo_formateado
        rut = rut[:-3]
    cuerpo_formateado = rut + cuerpo_formateado
    
    return f"{cuerpo_formateado}-{dv.upper()}"


def _translate(text: str, translate_to_en: bool = False) -> str:
    """Traduce un texto al inglés si está habilitado"""
    if not translate_to_en:
        return text
    
    for es, en in TRANSLATIONS.items():
        if es.lower() in text.lower():
            text = text.replace(es, en)
    
    return text


def parse_bhe_xml(xml: Union[str, bytes, Path], translate_to_en: bool = False) -> BHEData:
    """
    Parsea un XML de Boleta de Honorarios Electrónica
    
    Args:
        xml: Ruta al archivo XML o contenido en bytes
        translate_to_en: Si True, traduce los campos al inglés
    
    Returns:
        BHEData con los datos parseados
    """
    if isinstance(xml, (str, Path)):
        tree = ET.parse(str(xml))
        root = tree.getroot()
    else:
        root = ET.fromstring(xml)
    
    # Emisor
    rut_emisor = _text(root.find("rutEmisor"))
    dv_emisor = _text(root.find("dvEmisor"))
    nombre_emisor = _translate(_text(root.find("nombreEmisor"), "SERVICIOS PROFESIONALES Y CONSULTOR DE INFORMATICA"), translate_to_en)
    actividad_economica = _translate(_text(root.find("actividadEconomica")), translate_to_en)
    domicilio_emisor = _text(root.find("domicilioEmisor"))
    comuna_emisor = _text(root.find("comunaEmisor"))
    telefono_emisor = _text(root.find("telefonoEmisor"))
    
    # Receptor
    rut_receptor = _text(root.find("rutReceptor"))
    dv_receptor = _text(root.find("dvReceptor"))
    nombre_receptor = _text(root.find("nombreReceptor"))
    domicilio_receptor = _text(root.find("domicilioReceptor"))
    comuna_receptor = _text(root.find("comunaReceptor"))
    
    # Boleta
    numero_boleta = _text(root.find("numeroBoleta"))
    fecha_boleta = _text(root.find("fechaBoleta"))
    tipo_documento = _text(root.find("tipodoc"))
    fechor_gen = _text(root.find("FechorGen"))
    fechor_env = _text(root.find("FechorEnv"))
    codigo_alfa = _text(root.find("Codigoalfa"))
    
    # Montos
    total_honorarios = _int_text(root.find("totalHonorarios"))
    liquido_honorarios = _int_text(root.find("liquidoHonorarios"))
    impuesto_honorarios = _int_text(root.find("impuestoHonorarios"))
    porcentaje_impuesto = _int_text(root.find("porcentajeImpuesto"))
    retiene_emisor = _text(root.find("retieneEmisor"))
    
    # Items
    items: List[BHEItem] = []
    prestacion = root.find("prestacionServicios")
    if prestacion is not None:
        for item_el in prestacion.findall("item"):
            descripcion = _translate(
                _text(item_el.find("descripcionLinea")),
                translate_to_en
            )
            numero_linea = _int_text(item_el.find("numeroLinea"))
            valor_servicio = _int_text(item_el.find("valorServicio"))
            
            items.append(BHEItem(
                numero_linea=numero_linea,
                descripcion=descripcion,
                valor_servicio=valor_servicio
            ))
    
    return BHEData(
        rut_emisor=_format_rut(rut_emisor, dv_emisor),
        dv_emisor=dv_emisor,
        nombre_emisor=nombre_emisor,
        actividad_economica=actividad_economica,
        domicilio_emisor=domicilio_emisor,
        comuna_emisor=comuna_emisor,
        telefono_emisor=telefono_emisor,
        rut_receptor=_format_rut(rut_receptor, dv_receptor),
        dv_receptor=dv_receptor,
        nombre_receptor=nombre_receptor,
        domicilio_receptor=domicilio_receptor,
        comuna_receptor=comuna_receptor,
        numero_boleta=numero_boleta,
        fecha_boleta=fecha_boleta,
        tipo_documento=tipo_documento,
        fechor_gen=fechor_gen,
        fechor_env=fechor_env,
        codigo_alfa=codigo_alfa,
        total_honorarios=total_honorarios,
        liquido_honorarios=liquido_honorarios,
        impuesto_honorarios=impuesto_honorarios,
        porcentaje_impuesto=porcentaje_impuesto,
        retiene_emisor=retiene_emisor,
        items=items,
        traducir_al_ingles=translate_to_en
    )
