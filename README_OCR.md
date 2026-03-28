# Soporte OCR para Imágenes de Boletas

## Nueva funcionalidad agregada

Ahora puedes procesar **capturas de pantalla** y **imágenes** de boletas electrónicas usando OCR (Reconocimiento Óptico de Caracteres).

### Formatos soportados:
- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF

### Uso desde CLI:

```bash
# Procesar una captura de pantalla
sii-xml-pdf convert "Captura de pantalla 2026-03-27 230155.png"

# Procesar cualquier imagen
sii-xml-pdf convert boleta_escaneada.jpg
sii-xml-pdf convert foto_boleta.png -o resultado.txt
```

### ¿Qué hace el sistema?

1. **Detecta automáticamente** si el archivo es una imagen
2. **Extrae el texto** usando Tesseract OCR
3. **Busca patrones** comunes de boletas chilenas:
   - RUT del emisor
   - Folio/Número de documento
   - Fecha de emisión
   - Monto total
   - Código de autorización
4. **Muestra los datos extraídos** en consola

### Requisitos adicionales:

**En Windows:**
1. Instalar Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
2. Asegurarse de que tesseract esté en el PATH

**En Linux (Debian/Ubuntu):**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa
pip install pytesseract Pillow
```

**En macOS:**
```bash
brew install tesseract
pip install pytesseract Pillow
```

### Limitaciones:

- El OCR depende de la calidad de la imagen
- Funciona mejor con imágenes nítidas y buena resolución
- El texto debe estar claramente legible
- No genera PDF, solo extrae datos (por ahora)

### Ejemplo de salida:

```
📷 Procesando imagen con OCR: Captura de pantalla 2026-03-27 230155.png
✅ Datos extraídos: {'rut': '22.222.222-2', 'monto_total': 1251008.0, 'folio': 284380}
📝 Texto crudo:
Centro Hermanos SpA
R.U.T.: 22.222.222-2
FACTURA ELECTRÓNICA
Ferreteria y Materiales de Construccion
...
```

## Conversión XML a PDF (funcionalidad original)

```bash
# PDF en español
sii-xml-pdf convert bhe_23181893-30.xml -o output/boleta.pdf

# PDF en inglés
sii-xml-pdf convert bhe_23181893-30.xml -o output/boleta_en.pdf --translate
```
