from bs4 import BeautifulSoup
import requests

#Obtenemos el HTML de dolar hoy
URL_BASE = 'https://dolarhoy.com/'
pedido_obtenido = requests.get(URL_BASE)
html_obtenido = pedido_obtenido.text

#Parceamos el html
soup = BeautifulSoup(html_obtenido, "html.parser")

general_div = soup.find_all('div', class_='tile is-parent is-7 is-vertical')
#Creamos la logica para extraer los datos que luego guardaremos en un cvs
dic_dolar = {}

for parent_div in general_div:
    child_divs = parent_div.find_all('div', class_='tile is-child')
    for div in child_divs:

        if (div.a.text is not None) and ("Oficial" in div.a.text):
          dic_dolar[div.a.text] = {}
          print(dic_dolar)
          for div_values in div.find_all('div', class_='values'):
            for div_buy in div_values.find_all('div', class_='compra'):
              split_buy = div_buy.text.split("$")
              print(split_buy)

              
            for div_sell_wrapper in div_values.find_all('div', class_='venta'):
              for div_sell in div_sell_wrapper.find_all('div', class_='venta-wrapper'):
                split_sell = div_sell.text.split("$")
                print(split_sell)
            dic_dolar[div.a.text] = split_buy, split_sell
            print(dic_dolar)
  



