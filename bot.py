import os, telebot, threading
from telebot import types
from flask import Flask
from deep_translator import GoogleTranslator

# YANGI TARJIMON BOT TOKENI - QARZ BOTIGA UMUMAN ARALASHMAYDI
TOKEN = "8853408009:AAH4bxqWOpPhMrstnC7-sYgga7VZP1xEE-0"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Foydalanuvchilarning tarjima rejimini saqlash lug'ati
# 0 - Avtomatik, 1 - Rus-Uzb, 2 - Uzb-Rus
user_modes = {}

@app.route('/')
def home(): return "Tarjimon bot 24/7 faol!"

def klaviatura():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("🤖 Avtomatik Tarjima (Uzb 🔄 Rus)")
    btn2 = types.KeyboardButton("🇷🇺 Ruscha ➡️ 🇺🇿 O'zbekcha")
    btn3 = types.KeyboardButton("🇺🇿 O'zbekcha ➡️ 🇷🇺 Ruscha")
    markup.add(btn1, btn2, btn3)
    return markup

@bot.message_handler(commands=['start'])
def st(m):
    user_modes[m.from_user.id] = 0 # Standart rejim avtomatik
    yo_riqnomi = (
        "👋 *Salom! Men professional Tarjimon botman.*\n\n"
        "Matn yuboring, men uni tezkor va aniq tarjima qilib beraman.\n\n"
        "⚙️ *Hozirgi rejim:* Avtomatik Tarjima\n"
        "Pastdagi tugmalar orqali rejimni o'zgartirishingiz mumkin."
    )
    bot.send_message(m.chat.id, yo_riqnomi, parse_mode="Markdown", reply_markup=klaviatura())

@bot.message_handler(func=lambda msg: True)
def tx(m):
    txt, uid = m.text.strip(), m.from_user.id
    
    if txt == "🤖 Avtomatik Tarjima (Uzb 🔄 Rus)":
        user_modes[uid] = 0
        bot.send_message(m.chat.id, "✅ *Avtomatik tarjima rejimi yoqildi.*\nMatn yuboring, o'zim tilni aniqlab tarjima qilaman.", parse_mode="Markdown")
        return
    elif txt == "🇷🇺 Ruscha ➡️ 🇺🇿 O'zbekcha":
        user_modes[uid] = 1
        bot.send_message(m.chat.id, "✅ *Ruscha ➡️ O'zbekcha rejimi yoqildi.*\nRuscha gaplaringiz o'zbekchaga o'giriladi.", parse_mode="Markdown")
        return
    elif txt == "🇺🇿 O'zbekcha ➡️ 🇷🇺 Ruscha":
        user_modes[uid] = 2
        bot.send_message(m.chat.id, "✅ *O'zbekcha ➡️ Ruscha rejimi yoqildi.*\nO'zbekcha gaplaringiz rus tiliga o'giriladi.", parse_mode="Markdown")
        return

    if uid not in user_modes:
        user_modes[uid] = 0

    try:
        # 1-FUNKSIYA: AVTOMATIK TARJIMA (Chalkashtirmasdan aniqlash)
        if user_modes[uid] == 0:
            rus_harflari = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
            matn_kichik = txt.lower()
            rus_miqdori = sum(1 for c in matn_kichik if c in rus_harflari)
            
            # Agar matnda ruscha harflar bo'lsa yoki maxsus belgilar bo'lsa, demak u ruscha matn
            if rus_miqdori > 0 and any(c in matn_kichik for c in ['ы', 'ъ', 'ь', 'щ', 'э', 'я', 'ю', 'ч', 'ш']):
                tarjima = GoogleTranslator(source='ru', target='uz').translate(txt)
                bayroq = "🇺🇿 *O'zbekcha tarjimasi:*\n\n"
            else:
                tarjima = GoogleTranslator(source='uz', target='ru').translate(txt)
                bayroq = "🇷🇺 *Ruscha tarjimasi:*\n\n"

        # 2-FUNKSIYA: RUS ➡️ UZB
        elif user_modes[uid] == 1:
            tarjima = GoogleTranslator(source='ru', target='uz').translate(txt)
            bayroq = "🇺🇿 *O'zbekcha tarjimasi:*\n\n"

        # 3-FUNKSIYA: UZB ➡️ RUS
        elif user_modes[uid] == 2:
            tarjima = GoogleTranslator(source='uz', target='ru').translate(txt)
            bayroq = "🇷🇺 *Ruscha tarjimasi:*\n\n"

        bot.send_message(m.chat.id, f"{bayroq}{tarjima}", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(m.chat.id, "❌ Tarjimada xatolik bo'ldi. Matnni qayta kiriting.")

if __name__ == "__main__":
    import threading
    bot_thread = threading.Thread(target=lambda: bot.infinity_polling(timeout=20, long_polling_timeout=10))
    bot_thread.daemon = True
    bot_thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
