import argostranslate.package
import argostranslate.translate
import pyperclip
import sys

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
    # Simple heuristic: if text contains Cyrillic characters, translate to English
    return 'ru-en' if any(ord('а') <= ord(c) <= ord('я') or ord('А') <= ord(c) <= ord('Я') for c in text) else 'en-ru'

def translate_text(text):
    """Translate text between Russian and English"""
    direction = get_translation_direction(text)
    from_code, to_code = direction.split('-')
    
    # Get installed languages
    from_lang = next(lang for lang in argostranslate.translate.get_installed_languages() if lang.code == from_code)
    to_lang = next(lang for lang in argostranslate.translate.get_installed_languages() if lang.code == to_code)
    
    # Perform translation
    translation = from_lang.get_translation(to_lang)
    return translation.translate(text)

def main():
    # Download language packages if needed
    download_languages()
    
    print("Ожидание текста в файле input.txt...")
    
    try:
        # Read from input.txt
        with open('input.txt', 'r', encoding='utf-8') as f:
            text = f.read().strip()
            
        if not text:
            print("Файл input.txt пуст")
            return
            
        print(f"Получен текст для перевода: {text[:100]}...")
        
        # Translate the text
        translated = translate_text(text)
        print(f"Перевод выполнен")
        
        # Write to output.txt
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(translated)
            
        print("Перевод сохранен в output.txt")
        
    except FileNotFoundError:
        print("Ошибка: Файл input.txt не найден")
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main() 