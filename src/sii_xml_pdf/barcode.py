from pdf417 import encode, render_svg
import xml.etree.ElementTree as ET
import re


def clean_ted(ted_xml: str) -> str:
    """
    Limpia el bloque TED para que pueda ser codificado en PDF417.
    - Quita namespaces (ns0:, ns1:, etc)
    - Elimina xmlns="..."
    - Saca saltos de línea y espacios extra
    """
    s = ted_xml.strip()
    # Quitar xmlns y atributos de namespace
    s = re.sub(r'\sxmlns(:\w+)?="[^"]+"', '', s)
    # Quitar prefijos tipo ns0:
    s = re.sub(r'\bns\d+:', '', s)
    # Quitar espacios y saltos de línea excesivos
    s = re.sub(r">\s+<", "><", s)
    s = re.sub(r"\s+", " ", s)
    return s


def pdf417_svg_from_ted(ted_str: str, columns: int = None, scale: int = 2, ratio: int = 3) -> str:
    ted_clean = clean_ted(ted_str)
    
    # Ajustar columnas dinámicamente según longitud de datos
    # La librería pdf417 requiere mínimo 3 rows
    # Si columns es muy alto para pocos datos, falla
    if columns is None:
        # Calcular columnas óptimas basadas en longitud
        length = len(ted_clean)
        if length < 50:
            columns = 5
        elif length < 100:
            columns = 8
        elif length < 200:
            columns = 12
        else:
            columns = 17
    
    # Intentar codificar, si falla reducir columnas
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            codes = encode(ted_clean, columns=columns, security_level=0)
            break
        except ValueError as e:
            if "Data too short" in str(e) or "Minimum is 3 rows" in str(e):
                columns = max(3, columns - 3)  # Reducir columnas pero no menos de 3
                attempt += 1
            else:
                raise
    
    svg_tree = render_svg(codes, scale=scale, ratio=ratio)
    root = svg_tree.getroot()

    # Devolver como string para inyectar en el template
    return ET.tostring(root, encoding="unicode")
