# Probando-YOLO
Emite sonido al cerrar los ojos ; 
YOLO = algoritmo para detectar objetos en imágenes o vídeo

## Script: extract certificate expiration dates

Se agregó `extract_certificate_expirations.py` para:
- Leer todos los PDF de una carpeta.
- Buscar la fecha de expiración del certificado.
- Exportar los resultados a un archivo Excel (`.xlsx`).

### Requisitos
```bash
pip install pdfplumber pandas openpyxl
```

### Uso
```bash
python extract_certificate_expirations.py ./certificados ./salida/expiraciones.xlsx
```
