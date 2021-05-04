import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import base64
import requests
import json


def get_data_with_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # options.set_preference("general.useragent.override",
    #                       "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36")

    try:
        browser = webdriver.Chrome(chrome_options=options)
        browser.get('data:text/html;charset=utf-8,' + url)
        time.sleep(5)

        with open("index_selenium.html", "w") as file:
            file.write(browser.page_source)
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()

    with open("index_selenium.html") as file:
        src = file.read()

    # get hotels urls
    soup = BeautifulSoup(src, "lxml")

    hotels_cards = soup.find_all(
        "div", class_="panel-group  col-xs-48 col-sm-24 col-md-12")

    print(hotels_cards)


def get_data_file():
    marks_data_list = []
    with open("index_selenium.html") as file:
        src = file.read()

    # get hotels urls
    soup = BeautifulSoup(src, "lxml")

    panel_group = soup.find_all("div", class_="panel-group")

    for item_accordion in panel_group:

        panels = item_accordion.find_all("div", class_="panel")

        for item_panel in panels:
            item_panel_heading = item_panel.find("div", class_="panel-heading")
            # Getting image in bytes
            response = requests.get(item_panel_heading.h4.img.attrs['src'])
            # image encoding
            encoded_image = base64.b64encode(response.content)

            panel_collapse = item_panel.find("div", class_="panel-collapse")

            table = panel_collapse.find("table", class_="table")

            name_models_list = []
            for row in table.findAll("tr"):
                cells = row.findAll("td")
                arrAttrs = get_url_data(row.attrs["onclick"])
                arrAttrs.append(cells[0].text)
                # Получить парсинг модификаций
                soup_modification = get_modification(arrAttrs)
                # Получить модель
                name_models_list = get_data_models(soup_modification)
                print(name_models_list)

            marks_data_list.append({
                "name_marka": item_panel_heading.h4.text,
                "img_marka": encoded_image.decode("utf-8"),
                "name_models_list": name_models_list
            })
    with open("name_models_list.json", "w", encoding="utf-8") as file:
        json.dump(marks_data_list, file,
                  indent=4, ensure_ascii=False)


def get_data_models(soup):

    row = soup.find("div", class_="row")
    col_lg_12 = row.find("div", class_="col-lg-12")
    response = requests.get(
        "https://to.catalogs-parts.com/"+col_lg_12.img.attrs['src'])
    # image encoding
    encoded_image = base64.b64encode(response.content)

    col_lg_36 = row.find("div", class_="col-lg-36")
    table = col_lg_36.find("table", class_="table")

    models_list = []
    for row in table.findAll("tr"):
        if(row.attrs == {}):
            continue
        cells = row.findAll("td")
        cols = [ele.text.strip() for ele in cells]
        # Получить soup детали
        arrAttrs = get_url_data(row.attrs["onclick"])
        arrAttrs.append(cells[0].text)
        # Получить детали модели
        soup_details = get_soup_details(arrAttrs)
        details = get_data_details(soup_details)

        models_list.append({
            "model": [ele for ele in cols if ele],
            "details": details})
    modification = {
        "name_modification": col_lg_12.img.attrs['alt'],
        "img_modificsation": encoded_image.decode("utf-8"),
        "models": models_list
    }
    return modification


def get_data_details(soup):

    row = soup.find("div", class_="row")
    col_lg_12 = row.find("div", class_="col-lg-12")
    response = requests.get(
        "https://to.catalogs-parts.com/"+col_lg_12.img.attrs['src'])
    # image encoding
    encoded_image = base64.b64encode(response.content)

    col_lg_36 = row.find("div", class_="col-lg-36")
    table = col_lg_36.find("table", class_="table")

    details_list = []
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if(cells != []):

            details_list.append({
                "name_detail": cells[0].text,
                "articul": cells[1].a.text
            })

    return details_list


def get_url_data(atributes):
    return atributes.replace("modification_get(", "").replace("detail_get(", "").replace(
        ")", "").replace("'", "").split(",")


def get_modification(attrs):
    # var url = '/cat_scripts/get_modification.php?lang=' + lang + '&manufacturer_id=' + manufacturer_id + '&model_id=' + model_id + '&client=' + client;
    # client,lang,manufacturer_id,model_id
    url = "https://to.catalogs-parts.com/cat_scripts/get_modification.php?lang=ru" + \
        "&manufacturer_id=" + str(attrs[2]) + \
        "&model_id=" + str(attrs[3]) + "&client=" + \
        str(attrs[0])
    url = url.replace("'", "")
    print(url)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    try:
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(url)
        time.sleep(5)

        with open("index_"+attrs[4] + ".html", "w") as file:
            file.write(browser.page_source)
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()

    with open("index_"+attrs[4] + ".html") as file:
        src1 = file.read()

    # get hotels urls
    soup = BeautifulSoup(src1, "lxml")

    return soup


def get_soup_details(attrs):

    # function detail_load(client, lang, manufacturer_id, model_id, modification_id){$('#breadcrumbs').toggleClass('progress-bar progress-bar-striped active bread-color');
    # var url = '/cat_scripts/get_detail.php?lang=' + lang + '&manufacturer_id=' + manufacturer_id + '&model_id=' + model_id + '&modification_id=' + modification_id + '&client=' + client;
    url = "https://to.catalogs-parts.com/cat_scripts/get_detail.php?lang=ru" + \
        "&manufacturer_id=" + str(attrs[2]) + \
        "&model_id=" + str(attrs[3]) + "&modification_id=" + str(attrs[4]) + "&client=" + \
        str(attrs[0])
    url = url.replace("'", "")
    print(url)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    try:
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(url)
        time.sleep(5)

        with open("index_"+attrs[5] + ".html", "w") as file:
            file.write(browser.page_source)
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()

    with open("index_"+attrs[5] + ".html") as file:
        src1 = file.read()

    # get hotels urls
    soup = BeautifulSoup(src1, "lxml")

    return soup


def main():
    # get_data("https://www.tury.ru/hotel/most_luxe.php")

    # get_data_with_selenium(
    #    "https://to.catalogs-parts.com/#%7Bclient:1;page:manufacturer;lang:ru%7D")
    get_data_file()


if __name__ == '__main__':
    main()
