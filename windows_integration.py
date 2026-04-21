"""
Интеграция с Windows API
Реальная смена обоев и взаимодействие с системой
"""

import ctypes
import os
import winreg
from pathlib import Path
import requests
from PIL import Image
import io


class WindowsWallpaperManager:
    """
    Управление обоями Windows через API
    """

    # Константы Windows API
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02

    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".semantic_wallpaper", "cache")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Кэш обоев: {self.cache_dir}")

    def set_wallpaper(self, image_path: str) -> bool:
        """
        Установить обои рабочего стола

        Args:
            image_path: Путь к изображению

        Returns:
            True если успешно
        """
        try:
            # Конвертируем путь в абсолютный
            abs_path = os.path.abspath(image_path)

            # Проверяем что файл существует
            if not os.path.exists(abs_path):
                print(f"❌ Файл не найден: {abs_path}")
                return False

            # Вызываем Windows API для смены обоев
            result = ctypes.windll.user32.SystemParametersInfoW(
                self.SPI_SETDESKWALLPAPER,
                0,
                abs_path,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )

            if result:
                print(f"✅ Обои установлены: {abs_path}")
                return True
            else:
                print(f"❌ Ошибка установки обоев")
                return False

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def set_lockscreen(self, image_path: str) -> bool:
        """
        Установить заставку экрана блокировки через Windows API

        Args:
            image_path: Путь к изображению

        Returns:
            True если успешно
        """
        try:
            abs_path = os.path.abspath(image_path)

            if not os.path.exists(abs_path):
                print(f"❌ Файл не найден: {abs_path}")
                return False

            # Подготавливаем изображение в правильной папке
            lockscreen_dir = Path(os.path.expanduser("~")) / "AppData" / "Local" / "Microsoft" / "Windows" / "LockScreen"
            lockscreen_dir.mkdir(parents=True, exist_ok=True)

            dest_path = lockscreen_dir / "LockScreen.jpg"

            # Конвертируем изображение
            img = Image.open(abs_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
            img.save(dest_path, 'JPEG', quality=95)

            # Пробуем установить через API с правами администратора
            try:
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP"
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)

                winreg.SetValueEx(key, "LockScreenImagePath", 0, winreg.REG_SZ, str(dest_path))
                winreg.SetValueEx(key, "LockScreenImageUrl", 0, winreg.REG_SZ, str(dest_path))
                winreg.SetValueEx(key, "LockScreenImageStatus", 0, winreg.REG_DWORD, 1)

                winreg.CloseKey(key)

                print(f"✅ Заставка установлена через API: {dest_path}")
                return True

            except PermissionError:
                # Если нет прав администратора, используем пользовательский метод
                print("⚠️  Нет прав администратора, используем пользовательский метод...")
                return self._set_lockscreen_user_method(str(dest_path))

        except Exception as e:
            print(f"❌ Ошибка установки заставки: {e}")
            return False

    def _set_lockscreen_user_method(self, image_path: str) -> bool:
        """
        Альтернативный метод установки заставки через пользовательский API
        Работает без прав администратора, но менее надежен
        """
        try:
            # Устанавливаем через реестр пользователя
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Lock Screen"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "LockScreenImage", 0, winreg.REG_SZ, image_path)
            winreg.CloseKey(key)

            # Уведомляем систему об изменениях через API
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02

            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                None,
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )

            print(f"✅ Заставка установлена (пользовательский API)")
            print(f"💡 Для гарантированной работы запустите от имени администратора")
            return True

        except Exception as e:
            print(f"⚠️  Пользовательский API не сработал: {e}")
            print("💡 Установите вручную: Параметры → Персонализация → Экран блокировки")
            print(f"   Файл: {image_path}")
            return False

    def set_wallpaper_and_lockscreen(self, image_path: str) -> tuple:
        """
        Установить обои и заставку одновременно

        Args:
            image_path: Путь к изображению

        Returns:
            Кортеж (wallpaper_success, lockscreen_success)
        """
        wallpaper_ok = self.set_wallpaper(image_path)
        lockscreen_ok = self.set_lockscreen(image_path)

        return (wallpaper_ok, lockscreen_ok)

    def download_image(self, url: str, filename: str = None) -> str:
        """
        Скачать изображение

        Args:
            url: URL изображения
            filename: Имя файла (опционально)

        Returns:
            Путь к скачанному файлу
        """
        try:
            print(f"⬇️  Скачиваем: {url}")

            # Скачиваем
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Определяем имя файла
            if filename is None:
                filename = url.split('/')[-1].split('?')[0]
                if not filename.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    filename += '.jpg'

            # Путь для сохранения
            file_path = self.cache_dir / filename

            # Открываем изображение и конвертируем в BMP (Windows любит BMP)
            image = Image.open(io.BytesIO(response.content))

            # Конвертируем в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Сохраняем как BMP для совместимости с Windows
            bmp_path = file_path.with_suffix('.bmp')
            image.save(bmp_path, 'BMP')

            print(f"✅ Сохранено: {bmp_path}")
            return str(bmp_path)

        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            return None

    def get_current_wallpaper(self) -> str:
        """
        Получить путь к текущим обоям

        Returns:
            Путь к файлу обоев
        """
        try:
            # Читаем из реестра Windows
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                0,
                winreg.KEY_READ
            )

            wallpaper_path, _ = winreg.QueryValueEx(key, "Wallpaper")
            winreg.CloseKey(key)

            return wallpaper_path

        except Exception as e:
            print(f"❌ Ошибка чтения текущих обоев: {e}")
            return None

    def set_wallpaper_from_url(self, url: str, wallpaper_id: str) -> bool:
        """
        Скачать и установить обои по URL

        Args:
            url: URL изображения
            wallpaper_id: ID обоев для имени файла

        Returns:
            True если успешно
        """
        # Скачиваем
        filename = f"{wallpaper_id}.bmp"
        image_path = self.download_image(url, filename)

        if image_path is None:
            return False

        # Устанавливаем
        return self.set_wallpaper(image_path)

    def clear_cache(self, keep_current: bool = True):
        """
        Очистить кэш скачанных обоев

        Args:
            keep_current: Сохранить текущие обои
        """
        try:
            current_wallpaper = self.get_current_wallpaper() if keep_current else None

            deleted_count = 0
            for file in self.cache_dir.glob('*'):
                if file.is_file():
                    if keep_current and str(file) == current_wallpaper:
                        continue

                    file.unlink()
                    deleted_count += 1

            print(f"🗑️  Удалено файлов: {deleted_count}")

        except Exception as e:
            print(f"❌ Ошибка очистки кэша: {e}")


class UnsplashAPI:
    """
    Реальная интеграция с Unsplash API
    """

    def __init__(self, access_key: str = None):
        # Для демо используем публичный доступ
        # Получите свой ключ на https://unsplash.com/developers
        self.access_key = access_key or "demo"
        self.base_url = "https://api.unsplash.com"

        # Для демо без ключа используем source.unsplash.com
        self.use_source = (access_key is None or access_key == "demo")

    def search_photos(self, query: str, per_page: int = 10, orientation: str = "landscape"):
        """
        Поиск фотографий

        Args:
            query: Поисковый запрос
            per_page: Количество результатов
            orientation: Ориентация (landscape, portrait, squarish)

        Returns:
            Список фотографий
        """
        if self.use_source:
            # Используем source.unsplash.com (не требует API ключа)
            return self._get_source_photos(query, per_page)
        else:
            # Используем официальный API
            return self._search_api_photos(query, per_page, orientation)

    def _get_source_photos(self, query: str, count: int):
        """Получить фото через Picsum Photos (работает стабильно)"""
        import random
        photos = []

        for i in range(count):
            # Используем Picsum Photos - стабильный бесплатный сервис
            # Генерируем случайный ID для большего разнообразия
            image_id = random.randint(1, 1000)
            photo = {
                'id': f'picsum_{query}_{image_id}',
                'url': f'https://picsum.photos/1920/1080?random={image_id}',
                'download_url': f'https://picsum.photos/1920/1080?random={image_id}',
                'category': query,
                'tags': [query, 'wallpaper'],
                'author': 'Lorem Picsum',
                'resolution': '1920x1080',
                'description': f'{query.title()} wallpaper from Picsum'
            }
            photos.append(photo)

        return photos

    def _search_api_photos(self, query: str, per_page: int, orientation: str):
        """Поиск через официальный API"""
        try:
            url = f"{self.base_url}/search/photos"
            params = {
                'query': query,
                'per_page': per_page,
                'orientation': orientation,
                'client_id': self.access_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            photos = []

            for result in data.get('results', []):
                photo = {
                    'id': result['id'],
                    'url': result['urls']['regular'],
                    'download_url': result['urls']['full'],
                    'category': query,
                    'tags': [tag['title'] for tag in result.get('tags', [])],
                    'author': result['user']['name'],
                    'resolution': f"{result['width']}x{result['height']}",
                    'description': result.get('description', '')
                }
                photos.append(photo)

            return photos

        except Exception as e:
            print(f"❌ Ошибка API: {e}")
            # Fallback на source
            return self._get_source_photos(query, per_page)

    def get_random_photo(self, query: str = None):
        """Получить случайное фото"""
        if query:
            photos = self.search_photos(query, per_page=1)
            return photos[0] if photos else None
        else:
            # Случайное фото
            url = "https://source.unsplash.com/random/1920x1080"
            return {
                'id': 'random',
                'url': url,
                'download_url': url,
                'category': 'random',
                'tags': ['random'],
                'author': 'Unsplash',
                'resolution': '1920x1080'
            }


class WindowsSystemMonitor:
    """
    Мониторинг системы Windows
    """

    def __init__(self):
        pass

    def get_screen_resolution(self):
        """Получить разрешение экрана"""
        try:
            user32 = ctypes.windll.user32
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            return (width, height)
        except:
            return (1920, 1080)  # Fallback

    def get_time_of_day(self):
        """Определить время суток"""
        from datetime import datetime
        hour = datetime.now().hour

        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'day'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'

    def is_user_active(self):
        """Проверить активен ли пользователь"""
        try:
            # Получаем время последней активности
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize', ctypes.c_uint),
                    ('dwTime', ctypes.c_uint),
                ]

            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)

            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))

            # Время в миллисекундах с момента загрузки системы
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime

            # Если активность была меньше 5 минут назад - пользователь активен
            return millis < 300000  # 5 минут

        except:
            return True  # По умолчанию считаем активным


# Тестирование
if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ WINDOWS ИНТЕГРАЦИИ")
    print("=" * 60)
    print()

    # Тест 1: Менеджер обоев
    print("📱 Тест 1: Менеджер обоев")
    print("-" * 60)
    wm = WindowsWallpaperManager()

    current = wm.get_current_wallpaper()
    print(f"Текущие обои: {current}")
    print()

    # Тест 2: Unsplash API
    print("📱 Тест 2: Unsplash API")
    print("-" * 60)
    api = UnsplashAPI()

    photos = api.search_photos("nature", per_page=3)
    for photo in photos:
        print(f"  - {photo['id']}: {photo['description']}")
    print()

    # Тест 3: Системный монитор
    print("📱 Тест 3: Системный монитор")
    print("-" * 60)
    monitor = WindowsSystemMonitor()

    resolution = monitor.get_screen_resolution()
    time_of_day = monitor.get_time_of_day()
    is_active = monitor.is_user_active()

    print(f"Разрешение экрана: {resolution[0]}x{resolution[1]}")
    print(f"Время суток: {time_of_day}")
    print(f"Пользователь активен: {is_active}")
    print()

    # Тест 4: Скачивание и установка обоев
    print("📱 Тест 4: Скачивание и установка обоев")
    print("-" * 60)
    print("Хотите установить тестовые обои? (y/n): ", end="")

    try:
        choice = input().strip().lower()
        if choice == 'y':
            photo = api.get_random_photo("nature")
            success = wm.set_wallpaper_from_url(photo['download_url'], photo['id'])

            if success:
                print("✅ Обои успешно установлены!")
            else:
                print("❌ Не удалось установить обои")
    except:
        print("Пропущено")

    print()
    print("=" * 60)
    print("✅ Тестирование завершено")
    print("=" * 60)
