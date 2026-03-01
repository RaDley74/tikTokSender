import time
import os
import json
import random
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

TARGET_USER = os.getenv("TARGET_USER")

def get_random_message():
    # 1. Приветствия (35 вариантов)
    openings = [
        "Доброе утро", "Просыпайся", "С добрым утром", "Чудесного утра", "Самого светлого утра",
        "Прекрасного начала дня", "Малыш, доброе утро", "Солнышко встало", "Утренний привет",
        "Пусть твое утро будет добрым", "Эй, соня, пора вставать", "Лови мой утренний поцелуй",
        "Самого уютного утра", "Желаю бодрого утра", "Пусть рассвет тебя порадует", "Рассвет уже наступил",
        "С новым прекрасным днем", "Утречко доброе", "Светлого тебе пробуждения", "Пусть утро начнется с улыбки",
        "Пора открывать глазки", "Проснись и сияй", "Желаю нежного утра", "Пусть утро будет сказочным",
        "Свежего и бодрого утра", "Милая, пора вставать", "Самого теплого утра", "Пусть день начнется легко",
        "Шлю тебе заряд бодрости", "Улыбнись новому дню", "Утро обещает быть крутым", "Проснись, моя любовь",
        "Пусть это утро будет лучшим", "Энергичного тебе начала дня", "С первым лучом солнца"
    ]
    
    # 2. Обращения (35 вариантов)
    names = [
        "любимая", "радость моя", "моя жизнь", "звездочка моя", "счастье моё", "красавица",
        "невероятная", "родная", "моё вдохновение", "ангел мой", "принцесса", "милая", "моя королева",
        "нежность моя", "самая лучшая", "моё солнышко", "сокровище моё", "единственная моя",
        "очаровашка", "моя вселенная", "девочка моя", "чудо моё", "моя отрада", "прекрасная леди",
        "моя душа", "самая дорогая", "неповторимая", "валентинка моя", "моя мечта", "свет моих очей",
        "сердцу милая", "моя леди", "жемчужинка", "котенок", "ласточка моя"
    ]
    
    # 3. Пожелания (40 вариантов)
    wishes = [
        "пусть сегодня всё получается легко", "желаю самого вкусного кофе", "пусть день принесет только радость",
        "удачи во всех делах сегодня", "пусть работа пролетит незаметно", "сияй сегодня ярче всех",
        "помни, что я очень сильно тебя люблю", "пусть этот день будет особенным", "желаю море энергии и улыбок",
        "сегодня точно случится что-то хорошее", "пусть мир вокруг тебя сегодня улыбается",
        "жду нашей встречи с нетерпением", "пусть каждая минута будет наполнена счастьем",
        "пусть удача идет по пятам", "просто улыбнись этому дню", "пусть настроение будет на высоте",
        "желаю продуктивного и легкого дня", "пусть все планы реализуются", "сегодня твой день",
        "будь самой счастливой сегодня", "пусть гармония будет в каждом моменте", "наслаждайся этим днем",
        "пусть сегодня исполнятся маленькие мечты", "шлю тебе частичку своего тепла", "пусть день будет ярким",
        "улыбайся вопреки всему", "пусть день пройдет в ритме счастья", "будь полна сил до самого вечера",
        "пусть сегодня тебя окружают добрые люди", "желаю вдохновения в каждой мелочи",
        "пусть день будет продуктивным", "откройся новым возможностям", "пусть всё сложится идеально",
        "мечтай и воплощай", "пусть сегодня не будет повода для грусти", "пусть этот день станет легендарным",
        "твори и радуйся", "пусть вечер вознаградит за труды", "чувствуй мою поддержку всегда", "пусть сердце поет"
    ]
    
    # 4. Эмодзи (25 вариантов)
    emojis = [
        "☀️✨", "🥰💖", "🌹🕊️", "☕🥐", "🌈🌸", "💎🌟", "🦋💕", "🍭🍬", "🐣💌", "🔥❤️",
        "👑✨", "🍀🍀", "🎐🔮", "🌻🐝", "🥨🍓", "🥥🌴", "🌊🐚", "🧸🎀", "🏹💘", "⚡🔋",
        "🧘‍♀️🤍", "🦄💫", "🥂💃", "🎨🎭", "🚀🔝"
    ]

    # Собираем строку и возвращаем её
    return f"{random.choice(openings)}, {random.choice(names)}! {random.choice(wishes).capitalize()}. {random.choice(emojis)}"

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