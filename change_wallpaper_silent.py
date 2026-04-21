"""
Тихая смена обоев и заставки
Без GUI, без уведомлений, без терминала
Для использования в Task Scheduler
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def change_wallpaper_background():
    """
    Сменить обои и заставку в фоновом режиме
    Полностью незаметно для пользователя
    """
    try:
        from semantic_wallpaper_offline import OfflineWallpaperApp
        from windows_integration import WindowsWallpaperManager
        import random
        import io
        import contextlib

        # Перенаправляем весь вывод в никуда
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            # Создаем приложение
            app = OfflineWallpaperApp()

            # Получаем рекомендации
            recommendations = app.get_smart_recommendations()

            if not recommendations:
                return False

            # Выбираем СЛУЧАЙНЫЕ обои из рекомендаций
            wallpaper_id = random.choice(recommendations)
            wallpaper_data = app.knowledge_graph.graph.nodes[wallpaper_id]
            image_path = wallpaper_data.get('url')

            # Устанавливаем обои и заставку
            wm = WindowsWallpaperManager()

            # Обои
            wm.set_wallpaper(image_path)

            # Заставка (тихо, без вывода)
            try:
                wm.set_lockscreen(image_path)
            except:
                pass  # Игнорируем ошибки заставки

            # Записываем в граф
            app.knowledge_graph.record_interaction(
                app.current_user,
                wallpaper_id,
                'set_as_wallpaper'
            )

            # Сохраняем граф
            app.knowledge_graph.save('wallpaper_knowledge_graph.json')

            return True

    except Exception as e:
        # Тихо игнорируем ошибки
        return False


if __name__ == "__main__":
    # Запускаем в фоновом режиме
    # Без вывода, без окон, без уведомлений
    change_wallpaper_background()

    # Завершаемся без ожидания
    sys.exit(0)
