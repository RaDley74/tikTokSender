import time
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

TARGET_USER = os.getenv("TARGET_USER")
MESSAGE = os.getenv("MESSAGE")

def send_daily_message():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="tiktok_profile", 
            headless=True, # Оставляем False! Мы обойдем это через xvfb
            channel="chrome", 
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",           # Обязательно для серверов Linux
                "--disable-dev-shm-usage" # Решает проблему с памятью в Linux
            ], 
            viewport={'width': 1280, 'height': 720}
        )
        
        try:
            page = context.pages[0]

            print("Переходим в TikTok Messages...")
            page.goto("https://www.tiktok.com/messages", wait_until="networkidle")
            time.sleep(5) 

            print(f"Ищем чат с пользователем '{TARGET_USER}'...")
            
            try:
                chat_element = page.locator(f'[data-e2e="chat-list-item"]', has_text=TARGET_USER).first
                chat_element.wait_for(state="visible", timeout=10000)
                chat_element.click()
                print("✅ Чат найден и открыт!")
                time.sleep(3)
            except Exception:
                print(f"\n❌ ОШИБКА: Не удалось найти '{TARGET_USER}' в списке чатов слева!")
                return 

            print("Вводим сообщение...")
            chat_box = page.locator('div[contenteditable="true"]').first
            chat_box.wait_for(state="visible", timeout=5000)
            chat_box.click()
            page.keyboard.type(MESSAGE, delay=50) 
            time.sleep(1)

            print("Отправляем...")
            page.keyboard.press("Enter")
            
            print(f"✅ Сообщение для {TARGET_USER} успешно отправлено!")
            time.sleep(3) 

        except Exception as e:
            print(f"❌ Произошла непредвиденная ошибка: {e}")
        
        finally:
            context.close()

if __name__ == "__main__":
    send_daily_message()