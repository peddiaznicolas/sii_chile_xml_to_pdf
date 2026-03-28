"""
Módulo para extraer datos de boletas desde imágenes (OCR)
Soporta capturas de pantalla, PDFs escaneados, etc.
"""
import re
from PIL import Image
import pytesseract
from pathlib import Path
from typing import Optional, Dict, Any


def extract_text_from_image(image_path: str) -> str:
    """
    Extrae texto de una imagen usando OCR (Tesseract).
    
    Args:
        image_path: Ruta a la imagen (PNG, JPG, etc.)
    
    Returns:
        Texto extraído de la imagen
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='spa+eng')
        return text
    except Exception as e:
        raise RuntimeError(f"Error al procesar imagen con OCR: {str(e)}")


def parse_boleta_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Intenta parsear datos de una boleta desde texto extraído por OCR.
    
    Busca patrones comunes en boletas chilenas:
    - RUT emisor
    - Folio
    - Fecha
    - Monto total
    - Código de autorización
    
    Args:
        text: Texto extraído de la imagen
    
    Returns:
        Diccionario con los datos encontrados o None si no se pudo parsear
    """
    data = {}
    
    # Patrones comunes
    rut_pattern = r'(\d{1,2}\.\d{3}\.\d{3}-[\dK])|(\d{7,8}-[\dK])'
    fecha_pattern = r'(\d{2}/\d{2}/\d{4})'
    monto_pattern = r'\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)'
    folio_pattern = r'(?:Folio|N°|Numero)[:\s]*(\d+)'
    codigo_auth_pattern = r'(?:Código|Codigo)[:\s]*([A-Z0-9]{6,})'
    
    # Buscar RUT
    rut_matches = re.findall(rut_pattern, text)
    if rut_matches:
        # Tomar el primer RUT válido encontrado
        data['rut'] = rut_matches[0][0] if rut_matches[0][0] else rut_matches[0][1]
    
    # Buscar fecha
    fecha_matches = re.findall(fecha_pattern, text)
    if fecha_matches:
        data['fecha'] = fecha_matches[0]
    
    # Buscar monto total
    monto_matches = re.findall(monto_pattern, text)
    if monto_matches:
        # Limpiar formato de monto
        monto_str = monto_matches[-1].replace('.', '').replace(',', '.')
        try:
            data['monto_total'] = float(monto_str)
        except ValueError:
            pass
    
    # Buscar folio
    folio_matches = re.findall(folio_pattern, text, re.IGNORECASE)
    if folio_matches:
        data['folio'] = int(folio_matches[0])
    
    # Buscar código de autorización
    codigo_matches = re.findall(codigo_auth_pattern, text, re.IGNORECASE)
    if codigo_matches:
        data['codigo_autorizacion'] = codigo_matches[0]
    
    # Solo retornar si encontramos al menos algunos datos clave
    if len(data) >= 2:
        return data
    
    return None


def process_image_to_data(image_path: str) -> Dict[str, Any]:
    """
    Procesa una imagen y extrae datos estructurados de una boleta.
    
    Args:
        image_path: Ruta a la imagen
    
    Returns:
        Diccionario con los datos extraídos
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"La imagen no existe: {image_path}")
    
    # Extraer texto con OCR
    text = extract_text_from_image(image_path)
    
    # Parsear datos del texto
    data = parse_boleta_from_text(text)
    
    if not data:
        return {
            'success': False,
            'error': 'No se pudieron extraer datos de la boleta',
            'raw_text': text
        }
    
    return {
        'success': True,
        'data': data,
        'raw_text': text
    }
