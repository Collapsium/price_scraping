import requests, time, logging
from openpyxl import Workbook
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
#-WebDrivers
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options as EdgeOptions

class WebDriverException(Exception):
    pass

def get_soup_html(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_8_0; like Mac OS X) AppleWebKit/601.31 (KHTML, like Gecko) Chrome/55.0.2221.148 Mobile Safari/534.8"}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.content, 'html.parser')
    return soup


def get_webdriver():

    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')

    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")  # Run Chrome in headless mode

    edge_options = EdgeOptions()
    edge_options.add_argument("--headless")  # Run Chrome in headless mode

    try:
        chrome_driver = webdriver.Chrome(options=chrome_options, service=ChromeService(ChromeDriverManager().install()))
        return chrome_driver

    except WebDriverException as e:
        print("Chrome driver initialization failed:", str(e))

    try:
        firefox_driver = webdriver.Firefox(options=firefox_options, service = FirefoxService(GeckoDriverManager().install()))
        return firefox_driver

    except WebDriverException as e:
        print("Firefox driver initialization failed:", str(e))

    try:
        edge_driver = webdriver.Edge(options=edge_options,service=EdgeService(EdgeChromiumDriverManager().install()))
        return edge_driver

    except WebDriverException as e:
        print("Edge driver initialization failed:", str(e))


def format_excel(working_sheet):
    working_sheet[f'A{1}'] = "Marca"
    working_sheet[f'B{1}'] = "Modelo"
    working_sheet[f'C{1}'] = "Precio_Lista"
    working_sheet[f'D{1}'] = "Precio_Final"
    return working_sheet


def append_data(working_sheet, list):
    for x in list:
        working_sheet.append(x)

def suzuki(url):
    try:
        data = []
        links = []

        driver = get_webdriver()
        driver.get(url)
        WebDriverWait(driver, timeout=15).until(lambda d: d.find_element(By.CLASS_NAME, "btn-quote"))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()

        base_url ="https://www.suzuki.cl/"
        links_cotizar = soup.find_all("a", class_="btn-quote", href=True)
        #print(links_cotizar)

        for a in links_cotizar:
            id_url = a['href'].replace('/', '', 1)
            new_url = base_url + id_url
            links.append(new_url)

        #print(links)
        for link in links:
            soup = get_soup_html(link)
            time.sleep(0.6)
    #---Model
            nombre_div = soup.find_all("div", class_="itemCotizar--auto--detalle")
            if not nombre_div:
                continue

            nombre_label = nombre_div[0].find('label')
            model = nombre_label.contents[0]
    #---Price
            price_tags = soup.find_all("h5", class_="text-price-value")
            if price_tags:
                price_contents = price_tags[0].contents
                price = price_contents[0].replace(u'$\xa0', u'')

                final_price_contents = price_tags[2].contents
                final_price = final_price_contents[0].replace(u'$\xa0', u'')
            else:
                continue

            row = ["Suzuki", model, price, final_price]
            print(row)
            data.append(row)

        append_data(ws, data)
        print("Datos suzuki cargados")

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de suzuki")
        print(e)

def ford(url):
    try:
        data = []
        links = {}
        root_url = 'https://www.ford.cl/'
        soup = get_soup_html(url)

        models_card = soup.find_all("div", class_= "vehicleTile section")
        #print(models_card)
        #Porque el modelo completo se forma sumando strings, se asocia parte del modelo con su link
        links_cotizar = soup.find_all("a", class_="cta-button cta-button-primary" , href=True)
        models_names = soup.find_all("h6")

        for model_card in models_card:

            modelo_1 = model_card.find("strong").text

            id_url = model_card.find("a", class_="fds-primary-button fds-dark text-capitalize")['href']
            new_url = root_url + id_url

            links.update({modelo_1 : new_url})
        #print(links)


        for x in links:
            soup = get_soup_html(links[x])
            time.sleep(0.5)
            soup = soup.find("div", class_= "models-display")

            if not soup:
                continue

            soup = soup.find_all("div", class_ ="carousel-slide model")

            for item in soup:
    # --Model
                modelo_2 = item.find("h6")
                model = f"{x} {modelo_2.string}"

    #--Price
                span = item.find_all("span")

                if not span:
                    continue

                price = span[0].contents[0].strip().replace('$', '')
                final_price = span[1].contents[0].strip().replace('$', '') if len(span) >= 2 else 'N/A'
                #print("final price: " + final_price)
                row = ["Ford", model, price, final_price]
                print(row)
                data.append(row)
        append_data(ws,data)
        print("Datos Ford cargados")

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de Ford")
        print(e)

def nissan(url):
    try:

        links = {}
        data = []
        root_url = "https://www.nissan.cl"
        soup = get_soup_html(url)

        soup = soup.find("div", class_="grid-row list-outer")
        li_children = soup.find("ul", class_ ="list-item").find_all("li", recursive = False)

        for x in li_children:
            soup = x.find("a", class_="title-link")
            modelo = soup.string
            new_url = root_url + soup['href'].replace(".html", "") + "/precios.html"
            links.update( {modelo : new_url})
        #print(links)

        for x in links:
            soup = get_soup_html(links[x])
            time.sleep(0.5)
            soup = soup.find("div", class_="c_153")
            soup = soup.find_all("tr")
            #print(soup)

            for y in soup[1:]:
                tr = y.find_all("td")
                #print(tr[0].string + " " + tr[1].string)

        #--Model & Price
                if("nuevo" in x or "nueva" in x.lower()):
                    model = "Nuevo " + tr[0].string
                    price = tr[1].string.replace("$ ", "")
                    final_price = tr[2].string.replace("$ ", "")
                    #print("modelo: "+ model )
                    #print("precio: " +price)
                else:
                    model = tr[0].string
                    price = tr[1].string.replace("$ ", "")
                    final_price = tr[1].string.replace("$ ", "")
                    #print("modelo: "+ model )
                    #print("precio: " +price)
                row = ["Nissan", model, price, final_price]
                print(row)
                data.append(row)
        #print(data)

        append_data(ws, data)
        print("Datos Nissan cargados")
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de Nissan")
        print(e)

def mg(url):
    try:
        links = {}
        data = []
        root_url = "https://www.mgmotor.cl/"
        soup = get_soup_html(url)

        soup = soup.find("div", id="modelosFooter")
        a_children = soup.find_all("a", href=True)

        for x in a_children:
            model_1 = x.string + " "
            #print("modelo_1: " + model_1)
            url= x['href']

            #print("url: " + url)
            links.update( {model_1 : url})

        #print(links)
        for x in links:
            soup = get_soup_html(links[x])
            time.sleep(0.5)
            model_boxes = soup.find_all("div", class_="box-version-model")

            for y in model_boxes:

            #--model

                model_tag = y.find("h3")
                model_2 = model_tag.string

                model = x + model_2
                #print("model: "+ model)

            #--price

                price_tag = y.find("div", class_="fw-bold mb-2")
                price = price_tag.string.replace("$","")
                #print("price: " + price)

                final_price_tag = y.find("div", class_="precio-final")
                final_price = final_price_tag.string.replace("Precio: $", "").replace(" *" ,"")
                #print("final price: " + final_price)
                row = ["MG", model, price, final_price]
                data.append(row)
                print(row)

        data.append(row)

        append_data(ws, data)
        print("Datos MG cargados")
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de MG")
        print(e)

def fiat(url):
    try:
        links = []
        data = []
        soup = get_soup_html(url)
        soup = soup.find("div", class_="col-md-11 pb-3")
        a_tags = soup.find_all("a", href=True)

        for a in a_tags:
            href = a['href']
            href = href.replace(" ",'')

            links.append(href)

        for x in links:
            soup = get_soup_html(x)
            time.sleep(0.5)
            model_boxes = soup.find_all("div", {"class":["modellist"
                                                         , "version"]})
            #print(len(model_boxes))
            for y in model_boxes:
                if not y:
                    continue

                model = y.find(["h4","h3"], {"class":[ "modellist__name","version__name"]})
                model = model.text

                price = y.find("div", {"class": [ "modellist__price-secondary","version__price-secondary"]})

                if price:
                    price = price.text.partition("\n")[0].partition("$")[2].partition("(")[0].partition("+")[0]

                final_price= y.find("div", {"class": [ "modellist__final-price","version__final-price"]})

                if not final_price:
                    continue

                final_price = final_price.find("span").text.replace("$", "")
                row = ["Fiat", model, price, final_price]
                data.append(row)
                print(row)
        append_data(ws, data)
        print("Datos Fiat cargados")

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de Fiat")
        print(e)

def kia(url):
    try:
        links = []
        data = []
        root_url = "https://www.kia.cl"
        soup = get_soup_html(url)
        soup = soup.find(class_="cmp-experiencefragment cmp-experiencefragment--menu-promociones")
        a_tags = soup.find_all("a")

        for a_tag in a_tags:
            a_tag = root_url + a_tag['href']
            links.append(a_tag)

        for link in links:
            driver = get_webdriver()
            driver.get(link)
            WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, "cmp-kia-tabla-precios"))

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            time.sleep(0.3)
            tabla = soup.find("table", class_="cmp-kia-tabla-precios")

            if not tabla:
                continue

            tr_tags = tabla.find_all("tr")

            for x in tr_tags[1:]:
                td_tags = x.find_all("td")

                model = td_tags[0].text
                price = td_tags[1].text.replace("$", "").replace("*","")
                final_price = td_tags[-1].findChild().text.replace("$", "").replace("*", "")

                row = ["Kia", model, price, final_price]

                data.append(row)
                print(row)

        append_data(ws, data)
        print("Datos kia cargados")

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de kia")
        print(e)

def honda(url):
    try:
        links = {}
        data = []
        soup = get_soup_html(url)

        soup = soup.find("div", class_="msubmenu msubmenu1")
        a_tags = soup.find_all("a", class_=False)

        for a_tag in a_tags:
            new_url = a_tag['href']
            modelo_1 = a_tag.contents[1].string
            if len(str(new_url)) <= 3: #In case there is not a good href tag
                continue

            links.update({modelo_1: new_url})

        for link in links:
            driver = get_webdriver()
            driver.get(links[link])
            WebDriverWait(driver, timeout=15).until(lambda d: d.find_element(By.CLASS_NAME, "premium-table-wrap"))

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.close()

            time.sleep(0.3)
            tabla = soup.find("div", class_="premium-table-wrap")
            rows = tabla.find_all("tr", class_= "premium-table-row")


            if not rows:
                continue

            for y in rows[1:]:

                row_data = y.find_all("span", class_="premium-table-inner")

                modelo_1 = row_data[0].text
                modelo_2 = row_data[1].text
                model = modelo_1 + " " + modelo_2
                price = row_data[2].text.replace("$", "").partition("+")[0]
                final_price = row_data[-1].text.replace("$", "").partition("+")[0]

                row = ["Honda", model, price, final_price]
                data.append(row)
                print(row)
        append_data(ws, data)
        print("Datos Honda cargados")

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de Honda")
        print(e)

def hyundai(url):
    try:
        links_prices = []
        data = []

        driver = get_webdriver()
        driver.get(url)
        WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, "compara-card__info"))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        #buscar los links por modelo
        links = [modelo.find("a", href=True)['href'] for modelo in soup.find_all("div", class_="compara-card__img")]

        for model_link in links:
            soup = get_soup_html(model_link)
            time.sleep(0.5)
            #Para cada modelo, busca el link de sus respectivos precios
            tabs = soup.find("div", class_="tabs-modelos__list tabs").find_all("a")
            for tab in tabs:
                # Dejar texto en formato común  para poder evaluarlo con la misma lógica
                string = tab.string.replace(" ", "").lower()

                if string == "preciosyfinanciamiento":
                    tab = tab['href']
                    links_prices.append(tab)

        for prices_model_link in links_prices:
            soup = get_soup_html(prices_model_link)
            time.sleep(1)
            soup.find("table", class_="table table-bordered")
            table_rows = soup.find_all("tr")

            for table_row in table_rows[1:]:
                td = table_row.find_all("td")
                # modelo
                model = td[0].text.replace("\n", "")
                price = td[1].text.replace("\n", "").replace("$","")
                final_price = td[3].text.replace("\n", "").replace("$","")

                row = ["Hyundai", model, price, final_price]
                print(row)
                data.append(row)
        append_data(ws, data)
        print("Datos Hyundai cargados")

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de Hyundai")
        print(e)
    return

def volkswagen(url):
    try:
        links = []
        data = []
        root_url = "https://www.volkswagen.cl"

        soup = get_soup_html(url)
        soup = soup.find("div", class_="vw6-contentModelOverviewModelList__innerList")
        model_buttons = soup.find_all("div", class_ = "vw6-contentModelOverviewModelListModel__buttons")

        #Añadir links
        for button in model_buttons:
            button_ver_mas = button.find("a", href= True, class_= "vw6-kwcBasicLinkTagIntern vw6-kwcLinkIntern")['href']
            link_model = (root_url + button_ver_mas)
            model_soup = get_soup_html(link_model)
            time.sleep(0.5)

            tabla = model_soup.find("table", class_="standard")
            if not tabla:  # pagina que lleva a otra elección
                model_soup = model_soup.find("div", class_="vw6-contentModelOverviewModelList__innerList")
                model_buttons = model_soup.find_all("div", class_="vw6-contentModelOverviewModelListModel__buttons")

                for button in model_buttons:
                    button_ver_mas = button.find("a", href=True, class_="vw6-kwcBasicLinkTagIntern vw6-kwcLinkIntern")['href']
                    links.append(root_url + button_ver_mas)
            else:
                 links.append(link_model)

        print(links)

        #Para cada página del modelo:
        for link in links:

            model_soup = get_soup_html(link)
            time.sleep(1)
            tabla = model_soup.find("table", class_="standard")

            if not tabla:#pagina que lleva a otra elección
                continue


            tr_tags = tabla.find_all("tr")

            for table_row in tr_tags[1:]:
                td_tags = table_row.find_all("td")
                model = td_tags[0].string.replace("\n", "").strip()
                price = td_tags[1].string.replace("$", "").replace(" ", "").replace(",", ".").replace("\n", "")
                final_price = td_tags[-1].string.replace("$", "").replace(" ", "").replace(",", ".").replace("\n", "")

                row = ["Volkswagen", model, price, final_price]

                data.append(row)
                print(row)

        append_data(ws, data)

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("No se pudieron sacar los datos de Volkswagen")
        print(e)


    return 0
# URLS
suzuki_url = "https://www.suzuki.cl/modelos"
ford_url = "https://www.ford.cl/todos/"
nissan_url = "https://www.nissan.cl/vehiculos/nuevos-vehiculos.html"
mg_url = "https://www.mgmotor.cl/"
fiat_url = "https://www.fiat.cl/"
kia_url = "https://www.kia.cl/promociones.html"
honda_url = "https://www.honda.cl/"
hyundai_url = "https://www.hyundai.cl/nuestros-modelos/"
volkswagen_url = "https://www.volkswagen.cl/modelos"

wb = Workbook()
ws = wb.active
format_excel(ws)


#suzuki(suzuki_url)
#ford(ford_url)
#nissan(nissan_url)
#mg(mg_url)
#fiat(fiat_url)
#kia(kia_url)
#honda(honda_url)
#hyundai(hyundai_url)
volkswagen(volkswagen_url)


wb.save('car_prices.xlsx')
wb.close()