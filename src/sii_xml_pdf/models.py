from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    qty: float
    rate: float
    descripcion: str
    total: int
    codigo: str = "0"

class Referencia(BaseModel):
    tipo_doc_referencia: str
    tipo_doc_referencia_palabras: str
    folio_referencia: str
    fecha_referencia: str

class Impuesto(BaseModel):
    tipo: str
    tipo_palabras: str
    monto: int

class DTEData(BaseModel):
    # Emisor
    rut_proveedor: str
    razon_social: str
    giro_proveedor: Optional[str] = None
    direccion_proveedor: Optional[str] = None
    ciudad_proveedor: Optional[str] = None
    comuna_proveedor: Optional[str] = None

    # Receptor
    receptor_rut: str
    receptor_razon_social: str
    receptor_giro: Optional[str] = None
    receptor_direccion: Optional[str] = None
    receptor_ciudad: Optional[str] = None
    receptor_comuna: Optional[str] = None

    # Encabezado
    forma_pago: int
    forma_pago_palabras: str
    fecha_vencimiento: Optional[str] = None
    monto_neto: int
    monto_total: int
    monto_iva: int
    monto_exento: int
    numero_factura: str
    fecha_emision: str
    tipo_dte: int
    tipo_dte_palabras: str
    tipo_dte_abreviatura: str

    # Otros
    timbre_xml: str

    # Detalles
    items: List[Item]
    referencias: List[Referencia]
    impuestos: List[Impuesto]


class BHEItem(BaseModel):
    numero_linea: int
    descripcion: str
    valor_servicio: int


class BHEData(BaseModel):
    """Datos para Boleta de Honorarios Electrónica"""
    # Emisor
    rut_emisor: str
    dv_emisor: str
    nombre_emisor: str
    actividad_economica: str
    domicilio_emisor: str
    comuna_emisor: str
    telefono_emisor: str
    
    # Receptor
    rut_receptor: str
    dv_receptor: str
    nombre_receptor: str
    domicilio_receptor: str
    comuna_receptor: str
    
    # Boleta
    numero_boleta: str
    fecha_boleta: str
    tipo_documento: str
    fechor_gen: str
    fechor_env: str
    codigo_alfa: str
    
    # Datos de resolución (para código de barras)
    numero_resolucion: str = ""
    fecha_resolucion: str = ""
    
    # Timbre XML (para generar código de barras)
    timbre_xml: Optional[str] = None
    
    # Montos
    total_honorarios: int
    liquido_honorarios: int
    impuesto_honorarios: int
    porcentaje_impuesto: int
    retiene_emisor: str
    
    # Items
    items: List[BHEItem]
    
    # Traducción
    traducir_al_ingles: bool = False
