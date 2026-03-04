import asyncio
import aiofiles
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import config
from utils import save_state

async def get_all_category_urls(session):
    """Собирает ссылки на подразделы уникалок."""
    print(" Собираем список всех категорий ")
    try:
        async with session.get(config.BASE_URL) as response:
            # Проверяем, успешно ли загрузилась главная страница
            if response.status != 200: return []
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            links = set()
            main_content = soup.find('main') or soup
            # Перебираем все найденные на странице ссылки
            for a in main_content.find_all('a', href=True):
                href = a['href']
                # Оставляем только ссылки на разделы /us/, исключая страницы входа и регистрации
                if '/us/' in href and not any(x in href for x in ['Login', 'Register', 'Contact']):
                    full_url = urljoin(config.BASE_URL, href)
                    links.add(full_url.split('#')[0]) 
            
            # Формируем список только из тех ссылок, которые ведут на вложенные категории
            valid_categories = [l for l in links if len(l) > len(config.BASE_URL)]
            print(f" Найдено категорий: {len(valid_categories)}")
            return valid_categories
    except Exception as e:
        print(f" Ошибка сбора категорий: {e}")
        return []

async def fetch_page(session, url, state):
    """Скачивает и сохраняет одну HTML страницу."""
    # Проверяем в файле состояния, не была ли эта страница скачана в прошлые запуски
    if state["pages"].get(url) == "done": return
    
    name = url.rstrip('/').split('/')[-1]
    file_path = os.path.join(config.HTML_DIR, f"{name}.html")

    try:
        async with session.get(url) as response:
            # Если сервер ответил успешно, начинаем процесс записи файла
            if response.status == 200:
                html = await response.text()
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(html)
                state["pages"][url] = "done"
                save_state(state)
                print(f" Скачана страница: {name}")
                await asyncio.sleep(config.REQUEST_DELAY)
    except Exception as e:
        print(f" Ошибка на странице {url}: {e}")