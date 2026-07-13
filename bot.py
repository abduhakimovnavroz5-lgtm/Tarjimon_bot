import os, telebot, threading
from telebot import types
from flask import Flask
from deep_translator import GoogleTranslator, SingleTranslator

TOKEN = "8853408009:AAH4bxqWOpPhMrstnC7-sYgga7VZP1xEE-0"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_modes = {}

@app.route('/')
def home(): return "Tarjimon bot 24/7 faol!"

def klaviatura():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("🤖 Автомат (Uzb 🔄 Rus)")
    btn2 = types.KeyboardButton("🇷🇺 Русский ➡️ 🇺🇿 O'zbekcha")
    btn3 = types.KeyboardButton("🇺🇿 O'zbekcha ➡️ 🇷🇺 Русский")
    markup.add(btn1, btn2, btn3)
    return markup

@bot.message_handler(commands=['start'])
def st(m):
    user_modes[m.from_user.id] = 0
    yo_riqnomi = (
        "👋 *Salom! / Привет!*\n"
        "Men professional Tarjimon botman. / Я бот-переводчик.\n\n"
        "🇺🇿 *O'zbekcha:* Matn yuboring, men uni tarjima qilaman. "
        "Rejimni o'zgartirish uchun pastdagi tugmalardan foydalaning.\n\n"
        "🇷🇺 *Русский:* Отправьте текст для перевода. "
        "Для изменения режима используйте кнопки ниже.\n\n"
        "🤖 *Hozirgi rejim / Текущий режим:* Автомат"
    )
    bot.send_message(m.chat.id, yo_riqnomi, parse_mode="Markdown", reply_markup=klaviatura())

@bot.message_handler(func=lambda msg: True)
def tx(m):
    txt, uid = m.text.strip(), m.from_user.id
    
    if txt == "🤖 Автомат (Uzb 🔄 Rus)":
        user_modes[uid] = 0
        bot.send_message(m.chat.id, "🤖 *Автомат уlandi / Автоматический режим активен.*\n(Uzb 🔄 Rus)", parse_mode="Markdown")
        return
    elif txt == "🇷🇺 Русский ➡️ 🇺🇿 O'zbekcha":
        user_modes[uid] = 1
        bot.send_message(m.chat.id, "🇷🇺 ➡️ 🇺🇿 *Ruscha ➡️ O'zbekcha rejimi faol.*", parse_mode="Markdown")
        return
    elif txt == "🇺🇿 O'zbekcha ➡️ 🇷🇺 Русский":
        user_modes[uid] = 2
        bot.send_message(m.chat.id, "🇺🇿 ➡️ 🇷🇺 *O'zbekcha ➡️ Ruscha rejimi faol.*", parse_mode="Markdown")
        return

    if uid not in user_modes:
        user_modes[uid] = 0

    try:
        # 1-FUNKSIYA: AVTOMATIK TARJIMA (MUTLOQ XATOSIZ TIZIM)
        if user_modes[uid] == 0:
            # Google tizimi orqali matn qaysi tilda ekanligini aniqlaymiz
            aniqlangan_til = SingleTranslator().detect_language(txt)
            
            # Agar yozilgan matn rus tilida bo'lsa
            if aniqlangan_til == 'ru':
                tarjima = GoogleTranslator(source='ru', target='uz').translate(txt)
                bayroq = "🇺🇿 *O'zbekcha tarjimasi:*\n\n"
            # Agar o'zbek tilida yoki boshqa har qanday tilda bo'lsa ruschaga o'g'iradi
            else:
                tarjima = GoogleTranslator(source='uz', target='ru').translate(txt)
                bayroq = "🇷🇺 *Перевод на русский:*\n\n"

        # 2-FUNKSIYA: RUS ➡️ UZB
        elif user_modes[uid] == 1:
            tarjima = GoogleTranslator(source='ru', target='uz').translate(txt)
            bayroq = "🇺🇿 *O'zbekcha tarjimasi:*\n\n"

        # 3-FUNKSIYA: UZB ➡️ RUS
        elif user_modes[uid] == 2:
            tarjima = GoogleTranslator(source='uz', target='ru').translate(txt)
            bayroq = "🇷🇺 *Перевод на русский:*\n\n"

        bot.send_message(m.chat.id, f"{bayroq}{tarjima}", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(m.chat.id, "❌ Ошибка в переводе. / Tarjimada xatolik yuz berdi.")

if __name__ == "__main__":
    bot_thread = threading.Thread(target=lambda: bot.infinity_polling(timeout=20, long_polling_timeout=10))
    bot_thread.daemon = True
    bot_thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
