from collections import defaultdict
from bs4 import BeautifulSoup
import requests
import csv

#Obtenemos el HTML de dolar hoy
URL_BASE = 'https://dolarhoy.com/'
pedido_obtenido = requests.get(URL_BASE)
html_obtenido = pedido_obtenido.text

#Parceamos el html
soup = BeautifulSoup(html_obtenido, "html.parser")

general_div = soup.find_all('div', class_='tile is-parent is-7 is-vertical')
#Creamos la logica para extraer los datos que luego guardaremos en un cvs
dic_dolar = {}
fecha_div = soup.find('div', class_ = 'tile update')

for parent_div in general_div:
    child_divs = parent_div.find_all('div', class_='tile is-child')
    for div in child_divs:

        if (div.a.text is not None) and ("Oficial" in div.a.text):
          dic_dolar[div.a.text] = {}
          for div_values in div.find_all('div', class_='values'):
            for div_buy in div_values.find_all('div', class_='compra'):
              split_buy = div_buy.text.split("$")
              
            for div_sell_wrapper in div_values.find_all('div', class_='venta'):
              for div_sell in div_sell_wrapper.find_all('div', class_='venta-wrapper'):
                split_sell = div_sell.text.split("$")
            dic_dolar[div.a.text] = split_buy, split_sell
        elif (div.a.text is not None) and ("MEP/Bolsa" in div.a.text):
          dic_dolar[div.a.text] = {}
          for div_values in div.find_all('div', class_='values'):
            for div_buy in div_values.find_all('div', class_='compra'):
              split_buy = div_buy.text.split("$")
              
            for div_sell_wrapper in div_values.find_all('div', class_='venta'):
              for div_sell in div_sell_wrapper.find_all('div', class_='venta-wrapper'):
                split_sell = div_sell.text.split("$")
            dic_dolar[div.a.text] = split_buy, split_sell
        elif (div.a.text is not None) and ("liqui" in div.a.text):
          dic_dolar[div.a.text] = {}
          for div_values in div.find_all('div', class_='values'):
            for div_buy in div_values.find_all('div', class_='compra'):
              split_buy = div_buy.text.split("$")
              
            for div_sell_wrapper in div_values.find_all('div', class_='venta'):
              for div_sell in div_sell_wrapper.find_all('div', class_='venta-wrapper'):
                split_sell = div_sell.text.split("$")
            dic_dolar[div.a.text] = split_buy, split_sell
        elif (div.a.text is not None) and ("cripto" in div.a.text):
          dic_dolar[div.a.text] = {}
          for div_values in div.find_all('div', class_='values'):
            for div_buy in div_values.find_all('div', class_='compra'):
              split_buy = div_buy.text.split("$")
              
            for div_sell_wrapper in div_values.find_all('div', class_='venta'):
              for div_sell in div_sell_wrapper.find_all('div', class_='venta-wrapper'):
                split_sell = div_sell.text.split("$")
            dic_dolar[div.a.text] = split_buy, split_sell
        elif (div.a.text is not None) and ("Tarjeta" in div.a.text):
          dic_dolar[div.a.text] = {}
          for div_values in div.find_all('div', class_='values'):
            for div_buy in div_values.find_all('div', class_='compra'):
              split_buy = div_buy.text.split("$")
              
            for div_sell_wrapper in div_values.find_all('div', class_='venta'):
              for div_sell in div_sell_wrapper.find_all('div', class_='venta-wrapper'):
                split_sell = div_sell.text.split("$")
            dic_dolar[div.a.text] = split_buy, split_sell
print(dic_dolar)


fecha = fecha_div.text.split(" ")[2]
hora = fecha_div.text.split(" ")[3]
fecha_hora = fecha + " "+ hora
datos_restructurados = defaultdict(lambda: {"fecha": fecha_hora})
print(fecha_hora)

for tipo_dolar, (compra, venta) in dic_dolar.items():
    compra_valor = compra[1] if compra and len(compra) > 1 else "0"
    venta_valor = venta[1] if venta and len(venta) > 1 else "0"
    datos_restructurados[tipo_dolar]["Compra"] = "$" + compra_valor
    datos_restructurados[tipo_dolar]["Venta"] = "$" + venta_valor

# Escribir en el archivo CSV
with open('datos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    # Escribir encabezados
    headers = ['fecha']
    for tipo_dolar in datos_restructurados.keys():
        headers.extend([f"{tipo_dolar} Compra", f"{tipo_dolar} Venta"])
    writer.writerow(headers)
    
    # Escribir datos
    row = [fecha_hora]
    for tipo_dolar, valores in datos_restructurados.items():
        row.extend([valores["Compra"], valores["Venta"]])
    writer.writerow(row)

print("Datos guardados en datos.csv")