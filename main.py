import time
import os
import json
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

TARGET_USER = os.getenv("TARGET_USER")
MESSAGE = os.getenv("MESSAGE")

def send_daily_message():
    with sync_playwright() as p:
        # Запускаем браузер с дополнительными аргументами для стабильности в WSL
        browser = p.chromium.launch(
            headless=False, 
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--disable-gpu" # Часто помогает в WSL, если браузер падает
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        # --- УЛУЧШЕННАЯ ЗАГРУЗКА КУКИ ---
        if os.path.exists('cookies.json'):
            try:
                with open('cookies.json', 'r') as f:
                    cookies = json.load(f)
                    formatted_cookies = []
                    for c in cookies:
                        # Оставляем только те поля, которые Playwright гарантированно примет
                        clean = {k: v for k, v in c.items() if k in ['name', 'value', 'domain', 'path', 'expires', 'httpOnly', 'secure', 'sameSite']}
                        
                        # Исправляем SameSite (Strict, Lax, None)
                        if 'sameSite' in clean:
                            val = str(clean['sameSite']).capitalize()
                            clean['sameSite'] = val if val in ['Strict', 'Lax', 'None'] else 'Lax'
                        
                        # Исправляем домен (должен начинаться с точки для поддоменов)
                        if 'domain' in clean and 'tiktok.com' in clean['domain'] and not clean['domain'].startswith('.'):
                            clean['domain'] = ".tiktok.com"
                        
                        formatted_cookies.append(clean)
                    
                    context.add_cookies(formatted_cookies)
                print("✅ Куки загружены и нормализованы.")
            except Exception as e:
                print(f"❌ Ошибка в cookies.json: {e}")
                return

        page = context.new_page()

        try:
            print("Переходим в TikTok Messages...")
            # Используем 'commit' — это самый быстрый способ, не дожидаясь загрузки всех скриптов
            page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded", timeout=60000)
            
            # Ждем 10 секунд, чтобы увидеть, подхватилась ли сессия
            print("Ожидаем проверки авторизации...")
            time.sleep(10) 

            page.screenshot(path="check_auth.png")
            
            # Проверяем, не выкинуло ли на страницу логина
            if "login" in page.url or page.locator('text="Log in"').is_visible():
                print("❌ АВТОРИЗАЦИЯ НЕ УДАЛАСЬ: TikTok игнорирует ваши куки.")
                print("💡 СОВЕТ: Перевыгрузите cookies.json из Chrome (сначала выйдите и войдите в аккаунт).")
                return

            print(f"✅ Успех! Ищем чат с '{TARGET_USER}'...")
            
            # Ждем появления списка чатов
            page.wait_for_selector('[data-e2e="chat-list-item"]', timeout=15000)
            
            # Поиск чата (более гибкий)
            chats = page.locator('[data-e2e="chat-list-item"]')
            target_chat = None
            for i in range(chats.count()):
                text = chats.nth(i).inner_text()
                # Ищем по вхождению "Holly" или по первой части TARGET_USER
                if "Holly" in text or (TARGET_USER and TARGET_USER[:4] in text):
                    target_chat = chats.nth(i)
                    break
            
            if target_chat:
                target_chat.click()
                print("✅ Чат открыт.")
                time.sleep(3)
                
                print("Вводим сообщение...")
                chat_box = page.locator('div[contenteditable="true"]').first
                chat_box.click()
                page.keyboard.type(MESSAGE, delay=70)
                page.keyboard.press("Enter")
                print("🚀 Сообщение отправлено!")
                time.sleep(2)
            else:
                print("❌ Чат не найден в списке.")
                page.screenshot(path="not_found.png")

        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            if not page.is_closed():
                page.screenshot(path="last_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    send_daily_message()