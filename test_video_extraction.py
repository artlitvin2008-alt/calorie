"""
Тестовый скрипт для проверки извлечения кадров из видео
"""
import cv2
import numpy as np
import tempfile
import os
from pathlib import Path


def create_test_video(duration_sec=15, fps=30):
    """Создает тестовое видео с меняющимся цветом"""
    width, height = 640, 640
    total_frames = fps * duration_sec
    
    # Создаем временный файл
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    video_path = temp_file.name
    temp_file.close()
    
    # Создаем видео
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    
    print(f"Создаю тестовое видео: {duration_sec} сек, {fps} fps, {total_frames} кадров")
    
    for i in range(total_frames):
        # Меняем цвет кадра
        color = int(255 * (i / total_frames))
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = [color, color // 2, 255 - color]
        
        # Добавляем текст
        cv2.putText(
            frame, 
            f"Frame {i}/{total_frames}", 
            (50, 100), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (255, 255, 255), 
            2
        )
        
        out.write(frame)
    
    out.release()
    print(f"✅ Тестовое видео создано: {video_path}")
    return video_path


def extract_frames_test(video_path, num_frames=5):
    """Тестирует извлечение кадров"""
    print(f"\nИзвлекаю {num_frames} кадров из видео...")
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ Не удалось открыть видео")
        return []
    
    # Получаем параметры видео
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"Параметры видео: {total_frames} кадров, {fps} fps, {duration:.1f} сек")
    
    frames = []
    
    # Извлекаем кадры через равные промежутки
    for i in range(num_frames):
        # Время в секундах для кадра
        # Используем формулу: time = ((i + 1) / (num_frames + 1)) * duration
        time_sec = ((i + 1) / (num_frames + 1)) * duration
        
        # Устанавливаем позицию
        cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
        ret, frame = cap.read()
        
        if ret:
            frames.append(frame)
            print(f"✅ Извлечен кадр {i+1}/{num_frames} на {time_sec:.1f} сек")
        else:
            print(f"❌ Не удалось извлечь кадр {i+1}")
    
    cap.release()
    
    print(f"\n✅ Извлечено {len(frames)} кадров из {num_frames}")
    return frames


def test_mock_analyzer():
    """Тестирует мок-анализатор"""
    print("\n" + "="*50)
    print("Тестирую MockVideoNoteAnalyzer")
    print("="*50)
    
    import asyncio
    from handlers.video_notes import MockVideoNoteAnalyzer
    
    async def run_test():
        analyzer = MockVideoNoteAnalyzer()
        result = await analyzer.analyze_video_note(b"fake_video_bytes", 12345)
        
        print("\n📊 Результат анализа:")
        print(f"Блюдо: {result['dish_name']}")
        print(f"Компонентов: {len(result['components'])}")
        print(f"Калории: {result['calories_total']} ккал")
        print(f"Белки: {result['protein_g']}г")
        print(f"Жиры: {result['fat_g']}г")
        print(f"Углеводы: {result['carbs_g']}г")
        print(f"Транскрипция: {result['audio_transcription']}")
        print(f"Кадров: {result['frames_count']}")
        
        print("\n✅ MockVideoNoteAnalyzer работает корректно!")
    
    asyncio.run(run_test())


def main():
    """Основная функция"""
    print("🎥 Тест извлечения кадров из видео\n")
    
    # Создаем тестовое видео
    video_path = create_test_video(duration_sec=15, fps=30)
    
    try:
        # Извлекаем кадры
        frames = extract_frames_test(video_path, num_frames=5)
        
        if len(frames) == 5:
            print("\n✅ Все тесты пройдены успешно!")
        else:
            print(f"\n⚠️ Извлечено {len(frames)} кадров вместо 5")
        
        # Тестируем мок-анализатор
        test_mock_analyzer()
        
    finally:
        # Удаляем тестовое видео
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"\n🗑️ Тестовое видео удалено")


if __name__ == '__main__':
    main()
