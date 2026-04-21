"""
Менеджер обоев - единое приложение
Всё в одном месте с логичным меню
"""

import os
import sys
import ctypes
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def is_admin():
    """Проверить права администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def print_header(text):
    """Красивый заголовок"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)


def check_setup_status():
    """Проверить статус настройки"""
    import subprocess

    status = {
        'categories': False,
        'wallpapers': False,
        'auto_trigger': False,
        'weekly_update': False,
        'context_menu': False
    }

    # Проверяем категории
    config_file = Path.home() / ".semantic_wallpaper" / "categories.json"
    status['categories'] = config_file.exists()

    # Проверяем обои
    cache_dir = Path.home() / ".semantic_wallpaper" / "cache"
    if cache_dir.exists():
        wallpapers = list(cache_dir.glob('*.jpg')) + list(cache_dir.glob('*.bmp'))
        status['wallpapers'] = len(wallpapers) > 0

    # Проверяем триггеры
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-ScheduledTask -TaskName "SemanticWallpaperAutoChange" -ErrorAction SilentlyContinue'],
            capture_output=True,
            timeout=5
        )
        status['auto_trigger'] = result.returncode == 0
    except:
        pass

    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-ScheduledTask -TaskName "SemanticWallpaperWeeklyUpdate" -ErrorAction SilentlyContinue'],
            capture_output=True,
            timeout=5
        )
        status['weekly_update'] = result.returncode == 0
    except:
        pass

    # Проверяем контекстное меню
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\DesktopBackground\Shell\SemanticWallpaper")
        winreg.CloseKey(key)
        status['context_menu'] = True
    except:
        pass

    return status


def show_status(status):
    """Показать статус настройки"""
    print("\n📊 Текущий статус:")
    print(f"   {'✅' if status['categories'] else '❌'} Категории выбраны")
    print(f"   {'✅' if status['wallpapers'] else '❌'} Обои скачаны")
    print(f"   {'✅' if status['auto_trigger'] else '❌'} Автосмена обоев")
    print(f"   {'✅' if status['weekly_update'] else '❌'} Еженедельное обновление")
    print(f"   {'✅' if status['context_menu'] else '❌'} Контекстное меню")


def first_time_setup():
    """Первоначойка (мастер)"""
    print_header("🎉 МАСТЕР ПЕРВОНАЧАЛЬНОЙ НАСТРОЙКИ")

    print("\nДобро пожаловать! Настроим приложение за 3 шага:")
    print()

    # Шаг 1: Категории
    print("📂 Шаг 1/3: Выбор категорий")
    print("-" * 60)
    print("Сейчас откроется меню выбора категорий.")
    print("Выберите категории обоев которые вам нравятся.")
    print()
    input("Нажмите Enter для продолжения...")

    import subprocess
    subprocess.run([sys.executable, "setup_categories.py"])

    # Шаг 2: Скачивание обоев
    print()
    print("📥 Шаг 2/3: Скачивание обоев")
    print("-" * 60)
    print("Сейчас скачаем обои из выбранных категорий.")
    print()
    input("Нажмите Enter для продолжения...")

    subprocess.run([sys.executable, "update_from_categories.py"])

    # Шаг 3: Установка триггеров
    print()
    print("🤖 Шаг 3/3: Автоматизация")
    print("-" * 60)
    print("Настроим автоматическую смену обоев.")
    print()
    print("Что установить?")
    print("1. Всё (рекомендуется)")
    print("2. Только автосмену обоев")
    print("3. Только контекстное меню")
    print("4. Пропустить")
    print()

    choice = input("Ваш выбор: ").strip()

    if choice == '1':
        print("\n🔧 Установка всех компонентов...")
        print()

        if not is_admin():
            print("⚠️  Для полной функциональности нужны права администратора")
            print("Запустить с правами администратора? (y/n): ", end="")
            if input().strip().lower() == 'y':
                # Перезапускаем с правами администратора
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable,
                    f'"{__file__}" --install-all', None, 1
                )
                return

        subprocess.run([sys.executable, "setup_auto_trigger_ps.py"])
        print()
        subprocess.run([sys.executable, "setup_weekly_update.py"])
        print()
        subprocess.run([sys.executable, "context_menu_installer.py"])

    elif choice == '2':
        subprocess.run([sys.executable, "setup_auto_trigger_ps.py"])

    elif choice == '3':
        subprocess.run([sys.executable, "context_menu_installer.py"])

    print()
    print_header("✅ НАСТРОЙКА ЗАВЕРШЕНА")
    print("\n🎉 Всё готово! Обои будут меняться автоматически!")
    print()
    print("💡 Что дальше:")
    print("   • Обои меняются при включении/входе/выходе из сна")
    print("   • Библиотека обновляется каждое воскресенье")
    print("   • Можно сменить вручную через контекстное меню")
    print()


def main_menu():
    """Главное меню"""
    while True:
        print_header("🎨 МЕНЕДЖЕР ОБОЕВ")

        # Проверяем статус
        status = check_setup_status()
        show_status(status)

        print("\n" + "=" * 60)
        print("ГЛАВНОЕ МЕНЮ")
        print("=" * 60)

        # Если не настроено - предлагаем мастер
        if not all([status['categories'], status['wallpapers']]):
            print("\n⚠️  Приложение не настроено")
            print("\n0. 🎉 Мастер первоначальной настройки (рекомендуется)")
            print()

        print("НАСТРОЙКА:")
        print("1. 📂 Выбрать категории обоев")
        print("2. 📥 Скачать/обновить обои")
        print("3. 🤖 Настроить автосмену обоев")
        print("4. 📅 Настроить еженедельное обновление")
        print("5. 🖱️ Установить контекстное меню")
        print()
        print("ИСПОЛЬЗОВАНИЕ:")
        print("6. 🎨 Сменить обои сейчас")
        print("7. 📊 Статистика библиотеки")
        print("8. 🗑️ Управление библиотекой")
        print()
        print("СПРАВКА:")
        print("9. 📖 Показать документацию")
        print("Q. ❌ Выход")
        print("=" * 60)

        choice = input("\nВаш выбор: ").strip().lower()

        if choice == '0':
            first_time_setup()

        elif choice == '1':
            import subprocess
            subprocess.run([sys.executable, "setup_categories.py"])

        elif choice == '2':
            import subprocess
            subprocess.run([sys.executable, "update_from_categories.py"])

        elif choice == '3':
            import subprocess
            subprocess.run([sys.executable, "setup_auto_trigger_ps.py"])

        elif choice == '4':
            import subprocess
            subprocess.run([sys.executable, "setup_weekly_update.py"])

        elif choice == '5':
            import subprocess
            subprocess.run([sys.executable, "context_menu_installer.py"])

        elif choice == '6':
            print("\n🎨 Смена обоев...")
            import subprocess
            subprocess.run([sys.executable, "change_wallpaper_simple.py"])
            print("✅ Обои изменены!")
            input("\nНажмите Enter для продолжения...")

        elif choice == '7':
            show_library_stats()
            input("\nНажмите Enter для продолжения...")

        elif choice == '8':
            import subprocess
            subprocess.run([sys.executable, "manage_library.py"])

        elif choice == '9':
            show_documentation()
            input("\nНажмите Enter для продолжения...")

        elif choice == 'q':
            print("\n👋 До свидания!")
            break

        else:
            print("\n❌ Неверный выбор")
            input("Нажмите Enter для продолжения...")


def show_library_stats():
    """Показать статистику библиотеки"""
    print("\n📊 СТАТИСТИКА БИБЛИОТЕКИ")
    print("-" * 60)

    cache_dir = Path.home() / ".semantic_wallpaper" / "cache"

    if not cache_dir.exists():
        print("❌ Библиотека пуста")
        return

    jpg_files = list(cache_dir.glob('*.jpg'))
    bmp_files = list(cache_dir.glob('*.bmp'))

    total = len(jpg_files) + len(bmp_files)

    jpg_size = sum(f.stat().st_size for f in jpg_files) / (1024 * 1024)
    bmp_size = sum(f.stat().st_size for f in bmp_files) / (1024 * 1024)
    total_size = jpg_size + bmp_size

    print(f"Всего обоев: {total}")
    print(f"  • JPG: {len(jpg_files)} ({jpg_size:.1f} МБ)")
    print(f"  • BMP: {len(bmp_files)} ({bmp_size:.1f} МБ)")
    print(f"Общий размер: {total_size:.1f} МБ")
    print(f"Папка: {cache_dir}")

    # Показываем выбранные категории
    import json
    config_file = Path.home() / ".semantic_wallpaper" / "categories.json"

    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                categories = json.load(f)

            print(f"\nВыбранные категории: {len(categories)}")
            for cat in categories[:5]:
                cat_name = cat.split('/')[-2] if '/' in cat else cat
                print(f"  • {cat_name}")

            if len(categories) > 5:
                print(f"  ... и еще {len(categories) - 5}")
        except:
            pass


def show_documentation():
    """Показать документацию"""
    print("\n📖 ДОКУМЕНТАЦИЯ")
    print("-" * 60)
    print()
    print("Доступные файлы документации:")
    print()
    print("1. README.md - Главное руководство")
    print("2. QUICKSTART.md - Быстрый старт")
    print("3. HOW_TO_USE.md - Подробное использование")
    print("4. AUTO_TRIGGER_GUIDE.md - Автоматические триггеры")
    print("5. CATEGORIES_GUIDE.md - Работа с категориями")
    print()
    print("💡 Откройте эти файлы в текстовом редакторе")


def main():
    """Главная функция"""
    print_header("🎨 МЕНЕДЖЕР ОБОЕВ")
    print("\nСемантическое приложение для автоматической смены обоев")

    # Проверяем статус
    status = check_setup_status()

    # Если ничего не настроено - предлагаем мастер
    if not status['categories'] and not status['wallpapers']:
        print()
        print("👋 Похоже вы запускаете приложение впервые!")
        print()
        print("Запустить мастер настройки? (y/n): ", end="")

        if input().strip().lower() == 'y':
            first_time_setup()
            return

    # Иначе показываем главное меню
    main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 До свидания!")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
