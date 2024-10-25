import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
import os
import logging

# Configurar logging
logging.basicConfig(
    filename='informe_mensual.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def clean_date_column(df):
    """Limpia y formatea la columna de fecha"""
    try:
        # Eliminar filas con fechas inválidas
        df = df[~df['fecha'].str.contains('última vez:', case=False, na=False)]
        
        # Convertir a datetime con manejo de errores
        df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%y %H:%M', errors='coerce')
        
        # Eliminar filas con fechas nulas
        df = df.dropna(subset=['fecha'])
        
        return df
    except Exception as e:
        logging.error(f"Error al limpiar la columna de fecha: {str(e)}")
        raise

def parse_currency(value):
    """Convierte valores de moneda a float"""
    if pd.isna(value):
        return 0
    try:
        # Remover el símbolo de moneda y espacios
        value = str(value).replace('$', '').replace(' ', '')
        
        # Manejar diferentes formatos de números
        if ',' in value and '.' in value:
            # Formato con ambos símbolos (ej: 1.234,56)
            value = value.replace('.', '').replace(',', '.')
        elif ',' in value:
            # Formato con coma (ej: 1234,56)
            value = value.replace(',', '.')
            
        return float(value)
    except (ValueError, AttributeError):
        logging.warning(f"No se pudo convertir el valor: {value}")
        return 0

def generate_monthly_report(csv_file, output_pdf, end_date=None):
    """Genera el informe mensual en PDF"""
    try:
        logging.info("Iniciando generación del informe mensual")
        
        if end_date is None:
            end_date = datetime.now()
        
        # Leer y limpiar datos
        df = pd.read_csv(csv_file)
        df = clean_date_column(df)
        
        # Convertir columnas de valores a float
        for col in df.columns:
            if col != 'fecha':
                df[col] = df[col].apply(parse_currency)
        
        # Filtrar datos del mes
        last_day = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        first_day = last_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        df_month = df[(df['fecha'] >= first_day) & (df['fecha'] <= last_day)]
        
        if df_month.empty:
            raise ValueError(f"No hay datos para el período {first_day.strftime('%B %Y')}")
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(output_pdf, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph(f"Informe Mensual del Dólar - {first_day.strftime('%B %Y')}", styles['Title'])
        elements.append(title)
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
                try:
                    compra = f"${row[compra_col]:.2f}" if compra_col in row else '-'
                    venta = f"${row[venta_col]:.2f}" if venta_col in row else '-'
                    data.append([fecha, tipo, compra, venta])
                except Exception as e:
                    logging.warning(f"Error al procesar fila para {tipo}: {str(e)}")
                    continue
        
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

        # Agregar gráfico
        elements.append(PageBreak())
        elements.append(Paragraph("Gráfico de Evolución", styles['Heading2']))
        elements.append(Spacer(1, 12))

        plt.figure(figsize=(12, 8))
        for column in df_month.columns[1:]:
            if 'Venta' in column:
                plt.plot(df_month['fecha'], df_month[column], label=column.replace(' Venta', ''))
        
        plt.title('Evolución del Dólar (Venta) en el Último Mes')
        plt.xlabel('Fecha')
        plt.ylabel('Valor en Pesos')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=45)
        
        # Ajustar el rango del eje Y
        venta_cols = [col for col in df_month.columns if 'Venta' in col]
        if venta_cols:
            y_min = df_month[venta_cols].min().min()
            y_max = df_month[venta_cols].max().max()
            plt.ylim(y_min * 0.95, y_max * 1.05)  # Agregar un 5% de margen
            
            # Formatear el eje Y para mostrar valores en miles
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:.1f}k"))
        
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        graph_filename = 'temp_graph.png'
        plt.savefig(graph_filename, bbox_inches='tight', dpi=300)
        plt.close()
        
        elements.append(Image(graph_filename, width=700, height=400))
        
        # Generar PDF
        doc.build(elements)
        os.remove(graph_filename)
        
        logging.info(f"Informe generado exitosamente: {output_pdf}")
        
    except Exception as e:
        logging.error(f"Error al generar el informe: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        csv_file = 'datos_dolar.csv'
        output_pdf = f'informe_dolar_{datetime.now().strftime("%Y_%m")}.pdf'
        generate_monthly_report(csv_file, output_pdf)
        print(f"Informe mensual generado: {output_pdf}")
    except Exception as e:
        print(f"Error al generar el informe: {str(e)}")
        logging.error(f"Error al generar el informe: {str(e)}")