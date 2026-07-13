import os, telebot, threading
from telebot import types
from flask import Flask
from deep_translator import GoogleTranslator

TOKEN = "8853408009:AAH4bxqWOpPhMrstnC7-sYgga7VZP1xEE-0"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Vaqtincha tarjima qilinadigan matnlarni saqlash uchun lug'at
user_texts = {}

@app.route('/')
def home(): return "Tarjimon bot 24/7 faol!"

# Har safar matn kelganda uning tagida chiqadigan til tanlash tugmalari
def til_tanlash_klaviaturasi():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🇺🇿 O'zbekchaga / На узбекский", callback_data="to_uz")
    btn2 = types.InlineKeyboardButton("🇷🇺 Ruschaga / На русский", callback_data="to_ru")
    markup.add(btn1, btn2)
    return markup

@bot.message_handler(commands=['start'])
def st(m):
    yo_riqnomi = (
        "👋 *Salom! / Привет!*\n\n"
        "🇺🇿 *O'zbekcha:* Menga istalgan matnni yuboring, so'ngra uni qaysi tilga tarjima qilishni tugma orqali tanlang!\n\n"
        "🇷🇺 *Русский:* Отправьте мне любой текст, а затем выберите язык перевода с помощью кнопки!"
    )
    # Boshlang'ich menyu tugmalarini tozalab, faqat yo'riqnomani yuboramiz
    bot.send_message(m.chat.id, yo_riqnomi, parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda msg: True)
def xabar_keldi(m):
    uid = m.from_user.id
    txt = m.text.strip()
    
    # Kelgan matnni foydalanuvchi ID raqamiga biriktirib vaqtincha xotirada saqlaymiz
    user_texts[uid] = txt
    
    bot.send_message(
        m.chat.id, 
        "❓ *Qaysi tilga tarjima qilamiz? / На какой язык перевести?*", 
        parse_mode="Markdown", 
        reply_markup=til_tanlash_klaviaturasi()
    )

# --- INLINE TUGMALAR BOSILGANDA ISHLAYDIGAN QISM ---
@bot.callback_query_handler(func=lambda call: True)
def callback_boshqar(call):
    uid = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    
    # Agar foydalanuvchi yozgan matn xotirada saqlanmagan bo'lsa
    if uid not in user_texts:
        bot.answer_callback_query(call.id, "❌ Matn topilmadi. Qaytadan yuboring. / Текст не найден.")
        bot.delete_message(chat_id, msg_id)
        return

    txt = user_texts[uid]

    try:
        # Foydalanuvchi O'zbekchaga tarjima qilishni tanlasa
        if call.data == "to_uz":
            bot.answer_callback_query(call.id, "Tarjima qilinmoqda...")
            tarjima = GoogleTranslator(source='auto', target='uz').translate(txt)
            bayroq = "🇺🇿 *O'zbekcha tarjimasi:*\n\n"
            
        # Foydalanuvchi Ruschaga tarjima qilishni tanlasa
        elif call.data == "to_ru":
            bot.answer_callback_query(call.id, "Перевод...")
            tarjima = GoogleTranslator(source='auto', target='ru').translate(txt)
            bayroq = "🇷🇺 *Перевод на русский:*\n\n"

        # Savol bergan tugmali xabarni to'g'ridan-to'g'ri tayyor tarjimaga o'zgartiramiz
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=msg_id, 
            text=f"{bayroq}{tarjima}", 
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=msg_id, 
            text="❌ Ошибка в переводе. / Tarjimada xatolik yuz berdi."
        )

if __name__ == "__main__":
    bot_thread = threading.Thread(target=lambda: bot.infinity_polling(timeout=20, long_polling_timeout=10))
    bot_thread.daemon = True
    bot_thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
