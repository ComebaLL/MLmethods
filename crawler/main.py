import asyncio
import json
import os
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


BASE_URL = "https://poedb.tw/us/Unique_item"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DATA_DIR = "data"
HTML_DIR = os.path.join(DATA_DIR, "raw_html")
IMG_DIR = os.path.join(DATA_DIR, "images")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
REQUEST_DELAY = 1.0 


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"pages": {}, "images": {}}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4, ensure_ascii=False)

def ensure_folders():
    for folder in [HTML_DIR, IMG_DIR]:
        os.makedirs(folder, exist_ok=True)


# Сбор ссылок по категориям
async def get_all_category_urls(session):
    """Собирает ссылки на оружие, броню, бижутерию и т.д."""
    print(f" Собираем список всех категорий ")
    try:
        async with session.get(BASE_URL) as response:
            if response.status != 200: return []
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            links = set()
            # Ищем все ссылки в основном контенте, которые ведут на подразделы уникалок
            main_content = soup.find('main') or soup
            for a in main_content.find_all('a', href=True):
                href = a['href']
                # Фильтруем: только ссылки внутри /us/ и исключаем лишнее
                if '/us/' in href and not any(x in href for x in ['Login', 'Register', 'Contact']):
                    full_url = urljoin(BASE_URL, href)
                    links.add(full_url.split('#')[0]) 
            
            # Оставляем только те ссылки, которые длиннее базовой (чтобы попасть в подкатегории)
            valid_categories = [l for l in links if len(l) > len(BASE_URL)]
            print(f" Найдено категорий: {len(valid_categories)}")
            return valid_categories
    except Exception as e:
        print(f" Ошибка сбора категорий: {e}")
        return []


# Скачивание страниц
async def fetch_page(session, url, state):
    if state["pages"].get(url) == "done": return
    
    # Имя файла из последней части URL
    name = url.rstrip('/').split('/')[-1]
    file_path = os.path.join(HTML_DIR, f"{name}.html")

    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(html)
                state["pages"][url] = "done"
                save_state(state)
                print(f" Скачано: {name}")
                await asyncio.sleep(REQUEST_DELAY)
    except Exception as e:
        print(f" Ошибка на странице {url}: {e}")


# Загрузка картинок
async def download_image(session, img_url, alt_text, state):
    """Скачивает картинку, определяя расширение из ссылки."""
    if state["images"].get(img_url) == "done":
        return

    # Определяем расширение (webp, png или gif)
    parsed_url = urlparse(img_url)
    ext = os.path.splitext(parsed_url.path)[1] or ".webp"
    if "?" in ext: ext = ext.split("?")[0] # Убираем параметры если есть
    
    # Создание понятного имени файла
    # перебираем alt_text посимвольно
    # if c.isalnum() проверяем символ буква или цифра
    #  c in " _-" разрешаем символы 
    # .strip() удаляет лишние пробелы 
    clean_name = "".join(c for c in alt_text if c.isalnum() or c in " _-").strip()
    if not clean_name: 
        clean_name = os.path.basename(parsed_url.path).split('.')[0] or "item" # резервное название для файла из URL
    
    # Чтобы избежать дублей 
    url_hash = str(hash(img_url))[-6:] # создает короткое имя ссылки
    file_path = os.path.join(IMG_DIR, f"{clean_name}_{url_hash}{ext}") # путь куда будет сохранена картинка

    try:
        async with session.get(img_url) as response:
            if response.status == 200:
                content = await response.read()
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(content)
                state["images"][img_url] = "done"
                return True
    except:
        return False


async def main():
    ensure_folders()
    state = load_state()

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # Собираем категории 
        categories = await get_all_category_urls(session)
        
        # Скачиваем HTML 
        print(f" Проверка/Загрузка {len(categories)} HTML страниц ")
        for url in categories:
            await fetch_page(session, url, state)

        # Парсим локальные файлы
        print(" Анализ скачанных HTML страниц ")
        image_tasks = []
        
        # Список файлов в папке raw_html
        files = [f for f in os.listdir(HTML_DIR) if f.endswith(".html")]
        
        for file_name in files:
            path = os.path.join(HTML_DIR, file_name)
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                content = await f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Находим все картинки на странице
            all_imgs = soup.find_all('img')
            
            for img in all_imgs:
                # Проверка всех возможных атрибутов, где может быть ссылка
                src = img.get('data-src') or img.get('src') or img.get('data-lazy-src')
                if not src: continue
                
                # Фильтруем, нужны только картинки предметов
                src_lower = src.lower()
                is_item = any(x in src_lower for x in ['item', 'art/2ditems', 'web.poecdn.com', 'gen/image'])
                # Исключаем мелкий мусор
                is_trash = any(x in src_lower for x in ['favicon', 'logo', 'flag', 'facebook', 'twitter'])

                if is_item and not is_trash:
                    full_img_url = urljoin(BASE_URL, src)
                    alt = img.get('alt') or img.get('title') or ""
                    image_tasks.append(download_image(session, full_img_url, alt, state))

        # Загрузка
        if image_tasks: 
            print(f" Найдено ссылок: {len(image_tasks)}")
            
            final_tasks = [] # массив корутин готовых к запуску
            seen_urls = set() # мнж-во уникальных ссылок

            for img_url, alt in image_tasks:
                if img_url not in seen_urls:
                    seen_urls.add(img_url)
                    task = download_image(session, img_url, alt, state)
                    final_tasks.append(task)

            print(f" Уникальных картинок для загрузки: {len(final_tasks)}")
            
            # Ограничиваем количество одновременных соединений через Semaphore
            sem = asyncio.Semaphore(15)
            async def sem_task(task):
                async with sem:
                    return await task

            await asyncio.gather(*(sem_task(t) for t in final_tasks))
            save_state(state)
            print(" Все доступные картинки обработаны.")
        else:
            print(" Не найдено новых картинок для парсинга.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nОстановка")