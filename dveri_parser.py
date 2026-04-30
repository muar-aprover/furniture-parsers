from bs4 import BeautifulSoup
from curl_cffi import requests
import lxml, sys, csv, time, random, os, json
from tqdm import tqdm 
from check import save_checkpoint, load_checkpoint, delete_checkpoint

CHECKPOINT = "checkpoint.json"


url_catalog = "https://dveri.com/catalog/specialnye-dveri"
name_cataloga = url_catalog.split('/')[-1]
csv_file = f'data\\table_dveri\\dveri_{name_cataloga}.csv'

if not os.path.exists(csv_file):
    with open(csv_file, 'w', encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["№", "Название", "Цвет", "Размер", "Цена за полотно", "Цена за комплект", "Ссылка"])

page, item_index, n = load_checkpoint()

os.makedirs(f"data\\images\\dveri\\images_{name_cataloga}", exist_ok=True)   
session = requests.Session()
p_bare = tqdm(desc="Обработано", unit=" card")

while True:
    url = f'{url_catalog}?page={page}'
    try:
        req = session.get(url=url, impersonate='chrome')
        req.raise_for_status()
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(3)
        continue
    
    soup = BeautifulSoup(req.text, 'lxml')
    
    product_list = soup.find_all('div', class_='products__item')
    
    if not product_list:
        break
    with open(csv_file, 'a', encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        for idx in range(item_index, len(product_list)):
            product = product_list[idx]
            
            # Получение ссылки с общей страницы
            tag_link = product.find('a')
            link = "https://dveri.com" + tag_link.get('href') if tag_link and tag_link.get("href") else "Нет ссылки" # type: ignore
            
            # Получение фото продукта с общей страницы
            tag_img = product.find('img')
            if tag_img and tag_img.get('src'):
                resp_img = session.get(url=f'https://dveri.com{tag_img.get("src").replace("small", "large")}', impersonate='chrome')
                if resp_img.status_code == 200:
                    with open(f"data\\images\\dveri\\images_{name_cataloga}\\{n}.jpg", 'wb') as img_file:
                        img_file.write(resp_img.content)      
            
            # Получение названия с общей страницы
            tag_name = product.find(class_='card__title')
            name = tag_name.get_text(strip=True) if tag_name else "Нет названия"
            
            # Получение различных хар-тик продукта c страницы товара
            page_producta = session.get(url=link, impersonate='chrome')
            if page_producta.status_code != 200:
                save_checkpoint(page=page, item_index=idx + 1, n=n)
                continue
            
            page_soup = BeautifulSoup(page_producta.text, 'lxml') 
            
                # Получение цвета
            tag_colors = page_soup.find('div', class_="product__colors-switcher")
            list_colors = []
            
            if tag_colors:
                div_colors = tag_colors.find_all('img')
                for img_tag in div_colors:
                    list_colors.append(img_tag.get("data-tippy-content"))
            else:
                color = product.find(class_="card__color")
                get_color = color.get_text(strip=True) if color else None
                if get_color:  
                    list_colors.append(get_color)  
                else: 
                    list_colors.append("Цвет не указан")

                # Получение размеров
            tag_size = page_soup.find("div", class_="product__size-list")
            list_size = []
            if tag_size:
                div_size = tag_size.find_all("div")
                for size in div_size:
                    list_size.append(size.get_text(strip=True))
            else:
                list_size.append('Размер не указан')

                
                # Получение цены
                    # Получение цены за полотно с общей страницы
            price_polotno = product.find(class_="card__price")
            polotno = price_polotno.get_text(strip=True) if price_polotno else "Цена за полотно не указана"
                    # Получение цены за комлект с странице товара
            price_block = page_soup.find("div", class_="product__prices")
            tag_complect = price_block.find(class_="product__price") if price_block else None
            complect = tag_complect.get_text(strip=True) if tag_complect else "Цена за комлект не указана"

            row = [n, name, ", ".join(list_colors), ", ".join(list_size), polotno, complect, link]
            
            
            writer.writerow(row)
                
            save_checkpoint(page=page, item_index=idx + 1, n=n + 1)
            file.flush()
            n += 1
            p_bare.update(1)
            time.sleep(random.uniform(0.1, 0.6))
    
    page += 1
    item_index = 0
    save_checkpoint(page=page, item_index=item_index, n=n)
    
p_bare.close()   
print()
print("Парсинг завершен")

delete_checkpoint(CHECKPOINT)