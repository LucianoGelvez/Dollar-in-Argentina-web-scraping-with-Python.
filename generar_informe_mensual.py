import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
import os

def parse_currency(value):
    if pd.isna(value):
        return 0
    return float(value.replace('$', '').replace('.', '').replace(',', '.'))

def generate_monthly_report(csv_file, output_pdf, end_date=None):
    if end_date is None:
        end_date = datetime.now()
    
    df = pd.read_csv(csv_file)
    df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%y %H:%M')
    
    # Convertir columnas de valores a float
    for col in df.columns:
        if col != 'fecha':
            df[col] = df[col].apply(parse_currency)
    
    last_day = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    first_day = last_day.replace(day=1)
    df_month = df[(df['fecha'] >= first_day) & (df['fecha'] <= last_day)]
    
    doc = SimpleDocTemplate(output_pdf, pagesize=landscape(letter))
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Informe Mensual del Dólar - {first_day.strftime('%B %Y')}", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Crear la tabla
    data = [['Fecha', 'Tipo de Dólar', 'Compra', 'Venta']]
    tipos_dolar = {
        'Dólar blue': ('Dólar blue Compra', 'Dólar blue Venta'),
        'Dólar Oficial': ('Dólar Oficial Compra', 'Dólar Oficial Venta'),
        'Dólar MEP/Bolsa': ('Dólar MEP/Bolsa Compra', 'Dólar MEP/Bolsa Venta'),
        'Contado con liqui': ('Contado con liqui Compra', 'Contado con liqui Venta'),
        'Dólar cripto': ('Dólar cripto Compra', 'Dólar cripto Venta'),
        'Dólar Tarjeta': ('Dólar Tarjeta Compra', 'Dólar Tarjeta Venta')
    }
    
    for _, row in df_month.iterrows():
        fecha = row['fecha'].strftime('%Y-%m-%d')
        for tipo, (compra_col, venta_col) in tipos_dolar.items():
            compra = f"${row[compra_col]:.2f}" if compra_col in row else ''
            venta = f"${row[venta_col]:.2f}" if venta_col in row else ''
            data.append([fecha, tipo, compra, venta])
    
    table = Table(data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    elements.append(table)

    elements.append(PageBreak())
    elements.append(Paragraph("Gráfico de Evolución", styles['Heading2']))
    elements.append(Spacer(1, 12))

    plt.figure(figsize=(12, 8))
    for column in df.columns[1:]:
        if 'Venta' in column:
            plt.plot(df_month['fecha'], df_month[column], label=column.replace(' Venta', ''))
    
    plt.title('Evolución del Dólar (Venta) en el Último Mes')
    plt.xlabel('Fecha')
    plt.ylabel('Valor en Pesos')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xticks(rotation=45)
    
    # Ajustar el rango del eje Y
    y_min = df_month[[col for col in df_month.columns if 'Venta' in col]].min().min()
    y_max = df_month[[col for col in df_month.columns if 'Venta' in col]].max().max()
    plt.ylim(y_min * 0.95, y_max * 1.05)  # Agregar un 5% de margen
    
    # Formatear el eje Y para mostrar valores en miles
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:.1f}k"))
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    graph_filename = 'temp_graph.png'
    plt.savefig(graph_filename, bbox_inches='tight', dpi=300)
    plt.close()
    
    elements.append(Image(graph_filename, width=700, height=400))
    
    doc.build(elements)
    os.remove(graph_filename)

if __name__ == "__main__":
    csv_file = 'datos_dolar.csv'  # Asegúrate de que esta ruta sea correcta
    output_pdf = f'informe_dolar_{datetime.now().strftime("%Y_%m")}.pdf'
    generate_monthly_report(csv_file, output_pdf)
    print(f"Informe mensual generado: {output_pdf}")