import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import tempfile

# Función para exportar a Excel como archivo temporal
def exportar_a_excel(df):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    excel_path = temp_file.name
    temp_file.close()
    df.to_excel(excel_path, index=False)
    return excel_path

# Función para exportar a PDF como archivo temporal
def exportar_a_pdf(df):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    temp_file.close()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Reporte de Seguridad Ciudadana - San Isidro")
    c.drawString(100, 730, f"Total de Casos: {len(df)}")

    y_position = 700
    for index, row in df.head().iterrows():
        c.drawString(100, y_position, f"Caso {index + 1}: {row['TXTTIPOCASO']} - {row['FECCASO']}")
        y_position -= 20

    c.save()
    buffer.seek(0)

    with open(pdf_path, 'wb') as f:
        f.write(buffer.read())

    return pdf_path
