import asyncio
import os
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import config
from utils import ensure_folders, load_state, save_state
from html_loader import get_all_category_urls, fetch_page
from image_loader import download_image
from db_sync import sync_disk_to_db
from database import db_manager

async def main():
    ensure_folders()
    state = load_state()


    # Открытие соединения 
    async with aiohttp.ClientSession(headers=config.HEADERS) as session:
        
        # Сбор и скачивание HTML
        categories = await get_all_category_urls(session)
        print(f" Обработка {len(categories)} страниц категорий")
        # Проходим циклом по каждой найденной категории для сохранения её страницы
        for url in categories:
            await fetch_page(session, url, state)

        # Анализ локальных файлов
        print(" Анализ сохраненных файлов и поиск картинок")
        raw_image_data = [] 
        files = [f for f in os.listdir(config.HTML_DIR) if f.endswith(".html")]
        
        # Перебираем все сохраненные HTML-файлы для извлечения данных
        for file_name in files:
            path = os.path.join(config.HTML_DIR, file_name)
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(await f.read(), 'html.parser')
            
            # Ищем все теги изображений в текущем файле
            for img in soup.find_all('img'):
                src = img.get('data-src') or img.get('src') or img.get('data-lazy-src')
                # Если у тега отсутствует ссылка на источник, пропускаем его
                if not src: continue
                
                src_lower = src.lower()
                is_item = any(x in src_lower for x in ['item', 'art/2ditems', 'web.poecdn.com', 'gen/image'])
                is_trash = any(x in src_lower for x in ['favicon', 'logo', 'flag', 'facebook', 'twitter'])

                # Если картинка относится к предметам и не является мусорной иконкой, сохраняем её данные
                if is_item and not is_trash:
                    full_img_url = urljoin(config.BASE_URL, src)
                    alt = img.get('alt') or img.get('title') or ""
                    raw_image_data.append((full_img_url, alt))

        # Фильтрация и запуск скачивания картинок
        # Проверяем, были ли найдены подходящие ссылки в проанализированных файлах
        if raw_image_data:
            final_tasks = []
            seen_urls = set()

            # Цикл подготовки списка уникальных задач на скачивание
            for img_url, alt in raw_image_data:
                # Добавляем задачу только если ссылка уникальна для этого запуска и не была скачана ранее
                if img_url not in seen_urls and state["images"].get(img_url) != "done":
                    seen_urls.add(img_url)
                    task = download_image(session, img_url, alt, state)
                    final_tasks.append(task)

            # Проверяем, остались ли новые задачи после удаления всех дубликатов
            if not final_tasks:
                print(" Новых картинок не найдено.")
                return

            print(f" Начинаем скачивание {len(final_tasks)} новых картинок...")
            
            # Ограничиваем очередь через семафор
            sem = asyncio.Semaphore(config.MAX_CONCURRENT_DOWNLOADS)
            async def sem_task(task):
                async with sem: return await task

            await asyncio.gather(*(sem_task(t) for t in final_tasks))
            save_state(state)
            print(" Все задачи выполнены.")
        # Если в папке raw_html вообще не было найдено подходящих изображений
        else:
            print(" Данные для скачивания не найдены.")
    
    # Сохранение картинок в бд
    try:
        db_manager.connect()
        await sync_disk_to_db(state)
        save_state(state) # Финальное сохранение состояния
    finally:
        db_manager.close()
        

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма остановлена.")