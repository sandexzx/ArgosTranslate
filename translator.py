import argostranslate.package
import argostranslate.translate
import pyperclip
import sys
from langdetect import detect, LangDetectException
import os
import time

def download_languages():
    """Download language packages if not already installed"""
    print("Проверка установленных языков...")
    installed_languages = argostranslate.translate.get_installed_languages()
    installed_codes = {lang.code for lang in installed_languages}
    
    # Check if we have both Russian and English installed
    if 'ru' in installed_codes and 'en' in installed_codes:
        print("Все необходимые языковые пакеты уже установлены")
        for lang in installed_languages:
            print(f"- {lang.name} ({lang.code})")
        print()
        return
    
    print("Загрузка доступных языковых пакетов...")
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    print("Установка недостающих языковых пакетов...")
    # Download Russian and English language packages
    for package in available_packages:
        if package.from_code in ['ru', 'en'] and package.to_code in ['ru', 'en']:
            if package.from_code not in installed_codes or package.to_code not in installed_codes:
                print(f"Установка пакета: {package.from_name} -> {package.to_name}")
                package.install()
    
    print("Проверка установленных языков...")
    installed_languages = argostranslate.translate.get_installed_languages()
    print(f"Установлено языков: {len(installed_languages)}")
    for lang in installed_languages:
        print(f"- {lang.name} ({lang.code})")
    print()

def get_translation_direction(text):
    """Determine translation direction based on text language"""
    try:
        lang = detect(text)
        if lang == 'ru':
            return 'ru-en'
        elif lang == 'en':
            return 'en-ru'
        else:
            # If language is neither Russian nor English, default to English->Russian
            print(f"Предупреждение: Определен неизвестный язык ({lang}). Перевод будет выполнен с английского на русский.")
            return 'en-ru'
    except LangDetectException:
        # If language detection fails, use the old method
        return 'ru-en' if any(ord('а') <= ord(c) <= ord('я') or ord('А') <= ord(c) <= ord('Я') for c in text) else 'en-ru'

def translate_text(text):
    """Translate text between Russian and English"""
    try:
        direction = get_translation_direction(text)
        from_code, to_code = direction.split('-')
        
        # Get installed languages
        installed_languages = argostranslate.translate.get_installed_languages()
        installed_codes = {lang.code for lang in installed_languages}
        
        if from_code not in installed_codes:
            raise ValueError(f"Язык {from_code} не установлен. Пожалуйста, установите необходимые языковые пакеты.")
        if to_code not in installed_codes:
            raise ValueError(f"Язык {to_code} не установлен. Пожалуйста, установите необходимые языковые пакеты.")
        
        from_lang = next(lang for lang in installed_languages if lang.code == from_code)
        to_lang = next(lang for lang in installed_languages if lang.code == to_code)
        
        # Perform translation
        translation = from_lang.get_translation(to_lang)
        return translation.translate(text)
    except ValueError as e:
        print(f"Ошибка: {str(e)}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при переводе: {str(e)}")
        return None

def get_text_to_translate():
    """Get text from either clipboard or input.txt based on file modification time"""
    current_time = time.time()
    
    try:
        # Get file modification time
        file_mtime = os.path.getmtime('input.txt')
        time_diff = current_time - file_mtime
        
        if time_diff < 10:  # File was modified less than 10 seconds ago
            with open('input.txt', 'r', encoding='utf-8') as f:
                text = f.read().strip()
            print("Текст получен из файла input.txt")
            return text
        else:
            # Get text from clipboard
            text = pyperclip.paste().strip()
            print("Текст получен из буфера обмена")
            return text
            
    except FileNotFoundError:
        # If file doesn't exist, use clipboard
        text = pyperclip.paste().strip()
        print("Файл input.txt не найден, текст получен из буфера обмена")
        return text
    except Exception as e:
        print(f"Ошибка при получении текста: {str(e)}")
        return None

def main():
    # Download language packages if needed
    download_languages()
    
    print("Ожидание текста...")
    
    try:
        # Get text from either source
        text = get_text_to_translate()
        
        if not text:
            print("Не удалось получить текст для перевода")
            return
            
        print(f"Получен текст для перевода: {text[:100]}...")
        
        # Translate the text
        translated = translate_text(text)
        if translated:
            print(f"Перевод выполнен")
            
            # Write to output.txt
            with open('output.txt', 'w', encoding='utf-8') as f:
                f.write(translated)
                
            print("Перевод сохранен в output.txt")
        else:
            print("Перевод не выполнен")
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main() 