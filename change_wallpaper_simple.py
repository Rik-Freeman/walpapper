"""
Простая смена обоев (поддержка JPG и BMP)
Для Task Scheduler
"""

import sys
import os
import random
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def get_all_wallpapers():
    """Получить все обои (JPG и BMP)"""
    cache_dir = Path.home() / ".semantic_wallpaper" / "cache"
    test_dir = Path.home() / ".semantic_wallpaper" / "test_wallpapers"

    wallpapers = []

    # Из cache
    if cache_dir.exists():
        wallpapers.extend(cache_dir.glob('*.jpg'))
        wallpapers.extend(cache_dir.glob('*.jpeg'))
        wallpapers.extend(cache_dir.glob('*.bmp'))

    # Из test_wallpapers
    if test_dir.exists():
        wallpapers.extend(test_dir.glob('*.jpg'))
        wallpapers.extend(test_dir.glob('*.jpeg'))
        wallpapers.extend(test_dir.glob('*.bmp'))

    return list(wallpapers)


def change_wallpaper():
    """Сменить обои"""
    try:
        from windows_integration import WindowsWallpaperManager
        from datetime import datetime

        # Получаем все обои
        wallpapers = get_all_wallpapers()

        if not wallpapers:
            return False

        # Умный выбор по времени суток
        hour = datetime.now().hour

        # Фильтруем по категориям если возможно
        if 6 <= hour < 12:  # Утро
            preferred = [w for w in wallpapers if any(x in str(w).lower() for x in ['nature', 'minimal', 'landscape'])]
        elif 12 <= hour < 18:  # День
            preferred = [w for w in wallpapers if any(x in str(w).lower() for x in ['city', 'abstract'])]
        elif 18 <= hour < 22:  # Вечер
            preferred = [w for w in wallpapers if any(x in str(w).lower() for x in ['sunset', 'nature'])]
        else:  # Ночь
            preferred = [w for w in wallpapers if any(x in str(w).lower() for x in ['minimal', 'abstract', 'dark'])]

        # Если нашли подходящие - используем их, иначе все
        if preferred:
            wallpaper = random.choice(preferred)
        else:
            wallpaper = random.choice(wallpapers)

        # Устанавливаем
        wm = WindowsWallpaperManager()
        wm.set_wallpaper(str(wallpaper))

        # Заставка (тихо)
        try:
            wm.set_lockscreen(str(wallpaper))
        except:
            pass

        return True

    except Exception as e:
        # Тихо игнорируем ошибки
        return False


if __name__ == "__main__":
    change_wallpaper()
    sys.exit(0)
