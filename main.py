import time
import os
import json
import random
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

TARGET_USER = os.getenv("TARGET_USER")

def get_random_message():
    """Загружает список фраз из JSON и выбирает одну строку."""
    try:
        with open('messages.json', 'r', encoding='utf-8') as f:
            messages = json.load(f)
            # Если messages — это список списков, нам нужно добраться до строки
            choice = random.choice(messages)
            
            # Проверка: если вдруг выбрался список, берем его первый элемент
            if isinstance(choice, list):
                return str(choice[0])
            return str(choice)
            
    except Exception as e:
        print(f"❌ Ошибка при чтении messages.json: {e}")
        return "Доброе утро! Я тебя люблю! ❤️"

def send_daily_message():
    # Получаем случайную фразу
    message_to_send = get_random_message()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, 
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--disable-gpu"
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        # Загрузка куки
        if os.path.exists('cookies.json'):
            try:
                with open('cookies.json', 'r') as f:
                    cookies = json.load(f)
                    formatted_cookies = []
                    for c in cookies:
                        clean = {k: v for k, v in c.items() if k in ['name', 'value', 'domain', 'path', 'expires', 'httpOnly', 'secure', 'sameSite']}
                        if 'sameSite' in clean:
                            val = str(clean['sameSite']).capitalize()
                            clean['sameSite'] = val if val in ['Strict', 'Lax', 'None'] else 'Lax'
                        if 'domain' in clean and 'tiktok.com' in clean['domain'] and not clean['domain'].startswith('.'):
                            clean['domain'] = ".tiktok.com"
                        formatted_cookies.append(clean)
                    context.add_cookies(formatted_cookies)
                print("✅ Куки загружены.")
            except Exception as e:
                print(f"❌ Ошибка в cookies.json: {e}")
                return

        page = context.new_page()

        try:
            print("Переходим в TikTok Messages...")
            page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded", timeout=60000)
            
            print("Ожидаем проверки авторизации...")
            time.sleep(10) 

            if "login" in page.url or page.locator('text="Log in"').is_visible():
                print("❌ АВТОРИЗАЦИЯ НЕ УДАЛАСЬ.")
                return

            print(f"✅ Успех! Ищем чат с '{TARGET_USER}'...")
            page.wait_for_selector('[data-e2e="chat-list-item"]', timeout=15000)
            
            chats = page.locator('[data-e2e="chat-list-item"]')
            target_chat = None
            for i in range(chats.count()):
                text = chats.nth(i).inner_text()
                if "Holly" in text or (TARGET_USER and TARGET_USER[:4] in text):
                    target_chat = chats.nth(i)
                    break
            
            if target_chat:
                target_chat.click()
                print("✅ Чат открыт.")
                time.sleep(3)
                
                print(f"Отправляю: {message_to_send}")
                chat_box = page.locator('div[contenteditable="true"]').first
                chat_box.click()
                
                # Печатаем нашу случайную фразу
                page.keyboard.type(message_to_send, delay=70)
                page.keyboard.press("Enter")
                print("🚀 Сообщение успешно улетело!")
                time.sleep(2)
            else:
                print("❌ Чат не найден.")
                page.screenshot(path="not_found.png")

        except Exception as e:
            print(f"❌ Ошибка выполнения: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    send_daily_message()