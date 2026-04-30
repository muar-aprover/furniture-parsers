from bs4 import BeautifulSoup
from curl_cffi import requests
import lxml, sys, csv, time, random, os, json
from tqdm import tqdm 
from check import save_checkpoint, load_checkpoint, delete_checkpoint

CHECKPOINT = "checkpoint.json"

url_cataloga = "https://mebel.com/catalog/kukhni" #  <-- Вставить в кавычки ссылку на интересующий раздел

name_catalog = url_cataloga.split('/')
csv_file = f'data/table_mebel/list_item_{name_catalog[-1]}.csv'
os.makedirs(f"data/images/mebel/images_{name_catalog[-1]}", exist_ok=True)

if not os.path.exists(csv_file):
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as file_csv:
        writer = csv.writer(file_csv, delimiter=';')
        writer.writerow(['№', 'Ссылка', 'Стиль', 'Размер: В*Ш*Г', 'Цена'])
    
page, item_index, n = load_checkpoint()

progress = tqdm(desc="Обработано карточек", unit=" карточка")

session = requests.Session()
while True:
    
    url = f"{url_cataloga}?page={page}"


    try:
        req = session.get(url, impersonate='chrome', timeout=10)
        req.raise_for_status()
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(3)
        continue
    
    soup = BeautifulSoup(req.text, 'lxml')


    wrapper_list = soup.find_all('div', class_='card__wrapper')
    if not wrapper_list:
        break
        
    with open(csv_file, 'a', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for idx in range(item_index, len(wrapper_list)):
            card = wrapper_list[idx]
            
            a_tag = card.find("a")
            link_on_item = "https://mebel.com" + a_tag.get('href') if a_tag and a_tag.get('href') else "Не указана ссылка" # type: ignore
            
            tag_name = card.find('div', class_='card__name') # type: ignore
            style = tag_name.get_text(strip=True) if tag_name else "Имя/Стиль не указан"
            
            tag_size = card.find(class_='card__sizes') # type: ignore
            size = tag_size.get_text(strip=True).split()[-1] if tag_size and tag_size.text != " " else "Размер не указан"
            
            tag_price = card.find(class_='card__price') # type: ignore
            price = tag_price.get_text(strip=True) if tag_price else "Цена не указана"
            
            img_tag = card.find('img')
            if img_tag and img_tag.get('src'):
                img_url = img_tag.get('src')
                if img_url.startswith('/'): # type: ignore
                    img_url = "https://mebel.com" + img_url.replace('medium', 'large')
                img_req = session.get(img_url, impersonate='chrome')
                time.sleep(random.uniform(0.3, 0.7))
                if img_req.status_code == 200:
                    with open(f"data/images/mebel/images_{name_catalog[-1]}/{n}.jpg", "wb") as f:
                        f.write(img_req.content)
            
            row = [n, link_on_item, style, size, price] # type: ignore
            
            

            writer.writerow(row)
            
            save_checkpoint(page=page, item_index=idx + 1, n=n + 1)
            file.flush()
            n += 1
            progress.update(1)

            
    page += 1
    item_index = 0
    save_checkpoint(page=page, item_index=item_index, n=n)
    time.sleep(random.uniform(0.9, 1.6))
        
progress.close()
print()
print('Парсинг завершен')

delete_checkpoint(CHECKPOINT)