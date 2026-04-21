"""
Оффлайн версия семантического приложения
Использует локальные тестовые обои
"""

from semantic_wallpaper_app import (
    WallpaperKnowledgeGraph,
    SemanticRule,
    SemanticWallpaperApp
)
from windows_integration import (
    WindowsWallpaperManager,
    WindowsSystemMonitor
)
from pathlib import Path
import os
import sys
from datetime import datetime, timedelta
from typing import Dict
import time
import threading


class OfflineWallpaperApp(SemanticWallpaperApp):
    """
    Оффлайн версия с локальными обоями
    """

    def __init__(self, test_wallpapers_dir: str = None):
        # Путь к тестовым обоям - устанавливаем ДО вызова super().__init__()
        if test_wallpapers_dir is None:
            test_wallpapers_dir = os.path.join(
                os.path.expanduser("~"),
                ".semantic_wallpaper",
                "test_wallpapers"
            )

        self.test_wallpapers_dir = Path(test_wallpapers_dir)

        # Инициализируем базовое приложение
        super().__init__()

        # Добавляем Windows интеграцию
        self.wallpaper_manager = WindowsWallpaperManager()
        self.system_monitor = WindowsSystemMonitor()

        # Флаг для автоматического режима
        self.auto_mode_running = False
        self.auto_mode_thread = None

        print("🪟 Windows интеграция активирована")
        print(f"📁 Используем локальные обои: {self.test_wallpapers_dir}")

    def _load_initial_wallpapers(self):
        """Загрузить локальные тестовые обои"""
        print("📥 Загружаем локальные обои...")

        # Проверяем основную папку с кэшем
        cache_dir = Path(os.path.expanduser("~")) / ".semantic_wallpaper" / "cache"

        # Категории
        categories = {
            'nature': ['природа', 'пейзаж', 'зелень'],
            'city': ['город', 'архитектура', 'здания'],
            'abstract': ['абстракция', 'искусство', 'цвета'],
            'minimal': ['минимализм', 'простота', 'чистота'],
            'sunset': ['закат', 'небо', 'оранжевый'],
            'space': ['космос', 'звезды', 'галактика'],
            'mountains': ['горы', 'вершины', 'природа'],
            'ocean': ['океан', 'море', 'вода']
        }

        count = 0

        # Загружаем из test_wallpapers
        if self.test_wallpapers_dir.exists():
            for wallpaper_file in self.test_wallpapers_dir.glob('*.bmp'):
                filename = wallpaper_file.stem
                # Определяем категорию из имени файла
                category = filename.split('_')[0] if '_' in filename else 'unknown'

                self.knowledge_graph.add_wallpaper(
                    wallpaper_file.stem,
                    str(wallpaper_file),
                    category=category,
                    tags=categories.get(category, [category]),
                    author='Test',
                    resolution='1920x1080',
                    description=f'{category.title()} wallpaper'
                )
                count += 1

        # Загружаем из cache (скачанные обои)
        if cache_dir.exists():
            for wallpaper_file in cache_dir.glob('*.bmp'):
                filename = wallpaper_file.stem

                # Пропускаем если уже загружен
                if filename in self.knowledge_graph.graph:
                    continue

                # Определяем категорию из имени файла
                category = 'unknown'

                # Проверяем по имени файла
                filename_lower = filename.lower()
                for cat in categories.keys():
                    if cat in filename_lower:
                        category = cat
                        break

                # Если не нашли, пробуем по префиксу (picsum_nature_123)
                if category == 'unknown' and '_' in filename:
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        potential_cat = parts[1].lower()
                        if potential_cat in categories:
                            category = potential_cat

                self.knowledge_graph.add_wallpaper(
                    filename,
                    str(wallpaper_file),
                    category=category,
                    tags=categories.get(category, [category]),
                    author='Downloaded',
                    resolution='1920x1080',
                    description=f'{category.title()} wallpaper'
                )
                count += 1

        if count == 0:
            print(f"❌ Обои не найдены")
            print("💡 Запустите: python create_test_wallpapers.py")
            print("💡 Или: python expand_wallpaper_library.py")
        else:
            print(f"✅ Загружено {count} обоев")

            # Показываем статистику по источникам
            test_count = len(list(self.test_wallpapers_dir.glob('*.bmp'))) if self.test_wallpapers_dir.exists() else 0
            cache_count = count - test_count

            if test_count > 0:
                print(f"   📁 Тестовые: {test_count}")
            if cache_count > 0:
                print(f"   📥 Скачанные: {cache_count}")

    def change_wallpaper_real(self, wallpaper_id: str, change_lockscreen: bool = True) -> bool:
        """
        Реально сменить обои Windows

        Args:
            wallpaper_id: ID обоев
            change_lockscreen: Также сменить заставку экрана блокировки
        """
        try:
            # Получаем информацию об обоях из графа
            if wallpaper_id not in self.knowledge_graph.graph:
                print(f"❌ Обои не найдены: {wallpaper_id}")
                return False

            wallpaper_data = self.knowledge_graph.graph.nodes[wallpaper_id]
            file_path = wallpaper_data.get('url')  # В нашем случае это путь к файлу

            if not file_path:
                print(f"❌ Путь не найден для {wallpaper_id}")
                return False

            print(f"🖼️  Устанавливаем обои: {wallpaper_id}")
            print(f"   Категория: {wallpaper_data.get('category', 'Unknown')}")
            print(f"   Путь: {file_path}")

            # Устанавливаем обои и заставку
            if change_lockscreen:
                wallpaper_ok, lockscreen_ok = self.wallpaper_manager.set_wallpaper_and_lockscreen(file_path)

                if wallpaper_ok:
                    # Записываем в граф
                    self.knowledge_graph.record_interaction(
                        self.current_user,
                        wallpaper_id,
                        'set_as_wallpaper'
                    )

                    if lockscreen_ok:
                        print(f"✅ Обои и заставка установлены!")
                    else:
                        print(f"✅ Обои установлены!")
                        print(f"⚠️  Заставка не установлена (нужны права администратора)")

                    return True
                else:
                    print(f"❌ Не удалось установить обои")
                    return False
            else:
                # Только обои
                success = self.wallpaper_manager.set_wallpaper(file_path)

                if success:
                    # Записываем в граф
                    self.knowledge_graph.record_interaction(
                        self.current_user,
                        wallpaper_id,
                        'set_as_wallpaper'
                    )

                    print(f"✅ Обои установлены!")
                    return True
                else:
                    print(f"❌ Не удалось установить обои")
                    return False

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_smart_recommendations(self) -> list:
        """
        Умные рекомендации с учетом системного контекста
        """
        # Получаем системный контекст
        time_of_day = self.system_monitor.get_time_of_day()
        resolution = self.system_monitor.get_screen_resolution()

        print(f"🧠 Контекст: {time_of_day}, разрешение {resolution[0]}x{resolution[1]}")

        # Определяем предпочтения по времени суток
        time_preferences = {
            'morning': ['nature', 'minimal'],
            'day': ['city', 'abstract'],
            'evening': ['sunset', 'nature'],
            'night': ['minimal', 'abstract']
        }

        preferred_categories = time_preferences.get(time_of_day, ['nature'])

        # Находим обои из предпочитаемых категорий
        recommendations = []
        for category in preferred_categories:
            if category in self.knowledge_graph.graph:
                wallpapers = [
                    n for n in self.knowledge_graph.graph.predecessors(category)
                    if self.knowledge_graph.graph.nodes[n].get('type') == 'Wallpaper'
                ]
                recommendations.extend(wallpapers[:3])

        # Если нет рекомендаций, берем все
        if not recommendations:
            recommendations = [
                n for n in self.knowledge_graph.graph.nodes()
                if self.knowledge_graph.graph.nodes[n].get('type') == 'Wallpaper'
            ]

        return recommendations[:5]

    def start_auto_mode(self, interval_minutes: int = 1):
        """
        Запустить автоматический режим смены обоев
        """
        if self.auto_mode_running:
            print("⚠️  Автоматический режим уже запущен")
            return

        self.auto_mode_running = True

        def auto_change_loop():
            print(f"🔄 Автоматический режим запущен (интервал: {interval_minutes} мин)")

            while self.auto_mode_running:
                try:
                    # Получаем рекомендации
                    recommendations = self.get_smart_recommendations()

                    if recommendations:
                        # Выбираем первую рекомендацию
                        wallpaper_id = recommendations[0]

                        # Меняем обои
                        self.change_wallpaper_real(wallpaper_id)

                    # Ждем
                    for _ in range(interval_minutes * 60):
                        if not self.auto_mode_running:
                            break
                        time.sleep(1)

                except Exception as e:
                    print(f"❌ Ошибка в автоматическом режиме: {e}")
                    time.sleep(60)

            print("🛑 Автоматический режим остановлен")

        self.auto_mode_thread = threading.Thread(target=auto_change_loop, daemon=True)
        self.auto_mode_thread.start()

    def stop_auto_mode(self):
        """Остановить автоматический режим"""
        if self.auto_mode_running:
            self.auto_mode_running = False
            print("⏹️  Останавливаем автоматический режим...")
        else:
            print("⚠️  Автоматический режим не запущен")

    def interactive_menu(self):
        """Интерактивное меню"""
        while True:
            print("\n" + "=" * 60)
            print("СЕМАНТИЧЕСКОЕ ПРИЛОЖЕНИЕ ДЛЯ ОБОЕВ - ОФФЛАЙН РЕЖИМ")
            print("=" * 60)
            print("1. Получить рекомендации")
            print("2. Сменить обои и заставку (рекомендация)")
            print("3. Сменить обои и заставку (случайные)")
            print("4. Показать популярные")
            print("5. Лайкнуть текущие обои")
            print("6. Запустить автоматический режим")
            print("7. Остановить автоматический режим")
            print("8. Расширить библиотеку обоев")
            print("9. Перезагрузить библиотеку обоев")
            print("I. Установить контекстное меню")
            print("A. Статистика")
            print("B. Визуализировать граф")
            print("0. Выход")
            print("=" * 60)

            try:
                choice = input("Выберите действие: ").strip()

                if choice == '1':
                    recommendations = self.get_smart_recommendations()
                    print("\n📋 Рекомендации:")
                    for i, wallpaper_id in enumerate(recommendations, 1):
                        data = self.knowledge_graph.graph.nodes[wallpaper_id]
                        print(f"  {i}. {wallpaper_id}")
                        print(f"     Категория: {data.get('category')}")

                elif choice == '2':
                    recommendations = self.get_smart_recommendations()
                    if recommendations:
                        self.change_wallpaper_real(recommendations[0])
                    else:
                        print("❌ Нет рекомендаций")

                elif choice == '3':
                    # Случайные обои
                    all_wallpapers = [
                        n for n in self.knowledge_graph.graph.nodes()
                        if self.knowledge_graph.graph.nodes[n].get('type') == 'Wallpaper'
                    ]
                    if all_wallpapers:
                        import random
                        wallpaper_id = random.choice(all_wallpapers)
                        self.change_wallpaper_real(wallpaper_id)
                    else:
                        print("❌ Нет обоев")

                elif choice == '4':
                    trending = self.knowledge_graph.get_trending()
                    print("\n🔥 Популярные обои:")
                    if trending:
                        for i, wallpaper_id in enumerate(trending, 1):
                            data = self.knowledge_graph.graph.nodes[wallpaper_id]
                            print(f"  {i}. {wallpaper_id} - {data.get('category')}")
                    else:
                        print("  Пока нет популярных (используйте обои чтобы набрать статистику)")

                elif choice == '5':
                    current = self.wallpaper_manager.get_current_wallpaper()
                    print(f"Текущие обои: {current}")
                    print("❤️  Лайк!")

                elif choice == '6':
                    interval = input("Интервал смены (минуты, по умолчанию 1): ").strip()
                    interval = int(interval) if interval.isdigit() else 1
                    self.start_auto_mode(interval)

                elif choice == '7':
                    self.stop_auto_mode()

                elif choice == '8':
                    print("\n🔄 Запуск расширения библиотеки...")
                    import subprocess
                    subprocess.run([sys.executable, "expand_wallpaper_library.py"])
                    print("\n🔄 Перезагрузка библиотеки обоев...")

                    # Очищаем граф и перезагружаем
                    self.knowledge_graph.graph.clear()
                    self._load_initial_wallpapers()

                    print("✅ Библиотека обновлена!")

                elif choice == '9':
                    print("\n🔄 Перезагрузка библиотеки обоев...")

                    # Сохраняем историю взаимодействий
                    history = self.knowledge_graph.history.copy()

                    # Очищаем граф
                    self.knowledge_graph.graph.clear()

                    # Перезагружаем обои
                    self._load_initial_wallpapers()

                    # Восстанавливаем историю
                    self.knowledge_graph.history = history

                    # Показываем статистику
                    total = len([n for n in self.knowledge_graph.graph.nodes()
                                if self.knowledge_graph.graph.nodes[n].get('type') == 'Wallpaper'])

                    print(f"✅ Библиотека перезагружена! Всего обоев: {total}")

                elif choice.lower() == 'i':
                    print("\n🔧 Установка контекстного меню...")
                    import subprocess
                    subprocess.run([sys.executable, "context_menu_installer.py"])

                elif choice.lower() == 'a':
                    self.show_statistics()

                elif choice.lower() == 'b':
                    print("📊 Открываем визуализацию графа...")
                    self.visualize_graph()

                elif choice == '0':
                    print("👋 До свидания!")
                    self.stop_auto_mode()
                    break

                else:
                    print("❌ Неверный выбор")

            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                self.stop_auto_mode()
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()

    def show_statistics(self):
        """Показать статистику"""
        print("\n📊 СТАТИСТИКА")
        print("-" * 60)

        # Подсчитываем узлы по типам
        node_types = {}
        for node in self.knowledge_graph.graph.nodes():
            node_type = self.knowledge_graph.graph.nodes[node].get('type', 'Unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1

        for node_type, count in node_types.items():
            print(f"  {node_type}: {count}")

        # Подсчитываем взаимодействия
        interactions = len(self.knowledge_graph.history)
        print(f"\n  Всего взаимодействий: {interactions}")

        # Популярные категории
        print("\n  Популярные категории:")
        category_counts = {}
        for node in self.knowledge_graph.graph.nodes():
            if self.knowledge_graph.graph.nodes[node].get('type') == 'Wallpaper':
                category = self.knowledge_graph.graph.nodes[node].get('category')
                if category:
                    category_counts[category] = category_counts.get(category, 0) + 1

        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {category}: {count}")


def main():
    """Главная функция"""
    print("=" * 60)
    print("СЕМАНТИЧЕСКОЕ ПРИЛОЖЕНИЕ ДЛЯ ОБОЕВ")
    print("Оффлайн версия с локальными обоями")
    print("=" * 60)
    print()

    # Создаем приложение
    app = OfflineWallpaperApp()
    print()

    # Запускаем интерактивное меню
    app.interactive_menu()

    # Сохраняем граф при выходе
    app.knowledge_graph.save('wallpaper_knowledge_graph.json')
    print("💾 Граф знаний сохранен")


if __name__ == "__main__":
    main()
