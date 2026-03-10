import os
import aiofiles
import bson  # Нужен для преобразования байтов в формат MongoDB
from urllib.parse import urlparse
import config
import asyncio


async def download_image(session, img_url, alt_text, state, retries=3):
    """Скачивает картинку """
    if state["images"].get(img_url) == "done":
        return True

    parsed_url = urlparse(img_url)
    ext = os.path.splitext(parsed_url.path)[1] or ".webp"
    if "?" in ext: ext = ext.split("?")[0]
    
    # создание имени для файла, удаление запрещеных символов
    clean_name = "".join(c for c in alt_text if c.isalnum() or c in " _-").strip()
    if not clean_name: 
        clean_name = os.path.basename(parsed_url.path).split('.')[0] or "item"
    
    url_hash = str(hash(img_url))[-6:]
    file_name = f"{clean_name}_{url_hash}{ext}"
    file_path = os.path.join(config.IMG_DIR, file_name)
    

    # Скачивание картинок
    for attempt in range(retries):
        try:
            async with session.get(img_url, timeout=10) as response:
                if response.status == 200:
                    img_data = await response.read()
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(img_data)
                    
                    # Помечаем в стейте как скачанное на диск
                    state["images"][img_url] = "downloaded_to_disk" 
                    return True
        except Exception:
            if attempt < retries - 1:
                await asyncio.sleep(1)
                continue
    return False