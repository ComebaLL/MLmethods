import os
import aiofiles
from urllib.parse import urlparse
import config

async def download_image(session, img_url, alt_text, state):
    """Скачивает картинку и сохраняет в папку images."""
    # Проверяем по состоянию, не была ли эта картинка успешно скачана ранее
    if state["images"].get(img_url) == "done":
        return True

    parsed_url = urlparse(img_url)
    ext = os.path.splitext(parsed_url.path)[1] or ".webp"
    # Если в расширении файла остались параметры запроса (после знака вопроса), удаляем их
    if "?" in ext: ext = ext.split("?")[0]
    
    # Санитарная обработка имени
    clean_name = "".join(c for c in alt_text if c.isalnum() or c in " _-").strip()
    # Если после очистки описания имя файла оказалось пустым, используем название из ссылки
    if not clean_name: 
        clean_name = os.path.basename(parsed_url.path).split('.')[0] or "item"
    
    url_hash = str(hash(img_url))[-6:]
    file_path = os.path.join(config.IMG_DIR, f"{clean_name}_{url_hash}{ext}")

    try:
        async with session.get(img_url) as response:
            # Если запрос к серверу прошел успешно, записываем полученные данные в файл
            if response.status == 200:
                content = await response.read()
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(content)
                state["images"][img_url] = "done"
                return True
    except:
        return False