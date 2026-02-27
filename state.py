import time
from playwright.sync_api import sync_playwright

def run_auth():
    with sync_playwright() as p:
        # Используем persistent_context, чтобы данные сохранялись в папку автоматически
        context = p.chromium.launch_persistent_context(
            user_data_dir="tiktok_auth_profile", 
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        page = context.pages[0]
        page.goto("https://www.tiktok.com/login", wait_until="domcontentloaded")
        
        print("\n" + "="*50)
        print("ДЕЙСТВИЯ:")
        print("1. В терминале WSL сейчас появится скриншот 'auth_qr.png'.")
        print("2. Откройте его и отсканируйте QR-код телефоном.")
        print("3. Либо введите логин/пароль вручную (если используете GUI).")
        print("4. После входа нажмите Enter в этом терминале.")
        print("="*50 + "\n")

        # Делаем скриншот с QR-кодом каждые 5 секунд, чтобы вы могли его увидеть
        for _ in range(12): # Ждем минуту
            page.screenshot(path="auth_qr.png")
            if page.url == "https://www.tiktok.com/messages" or "messages" in page.url:
                print("✅ Система зафиксировала вход в сообщения!")
                break
            time.sleep(5)
        
        input("Нажмите Enter после того, как успешно авторизуетесь на сайте...")
        
        # Дополнительно сохраняем куки в отдельный файл на всякий случай
        cookies = context.cookies()
        import json
        with open('cookies.json', 'w') as f:
            json.dump(cookies, f)
        
        print("✅ Данные авторизации сохранены в папку 'tiktok_auth_profile' и файл 'cookies.json'")
        context.close()

if __name__ == "__main__":
    run_auth()