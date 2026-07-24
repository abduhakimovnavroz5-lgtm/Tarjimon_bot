import os
import telebot
import threading
from telebot import types
from flask import Flask
from deep_translator import GoogleTranslator

# TOʻGʻRILANGAN TOKEN: Ortiqcha qoʻshtirnoq va raqamlar olib tashlandi
TOKEN = "8853408009:AAFw9F9o2PbHwfDYH8WQiJVZfMNcV3Y22U0"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Vaqtincha tarjima qilinadigan matnlerns saqlash uchun lug'at
user_texts = {}

@app.route('/')
def home(): 
    return "Tarjimon bot 24/7 faol!"

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
    bot.send_message(m.chat.id, yo_riqnomi, parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda msg: True)
def xabar_keldi(m):
    uid = m.from_user.id
    txt = m.text.strip()
    
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
    
    if uid not in user_texts:
        bot.answer_callback_query(call.id, "❌ Matn topilmadi. Qaytadan yuboring. / Текст не найден.")
        bot.delete_message(chat_id, msg_id)
        return

    txt = user_texts[uid]

    try:
        if call.data == "to_uz":
            bot.answer_callback_query(call.id, "Tarjima qilinmoqda...")
            tarjima = GoogleTranslator(source='auto', target='uz').translate(txt)
            bayroq = "🇺🇿 *O'zbekcha tarjimasi:*\n\n"
            
        elif call.data == "to_ru":
            bot.answer_callback_query(call.id, "Перевод...")
            tarjima = GoogleTranslator(source='auto', target='ru').translate(txt)
            bayroq = "🇷🇺 *Перевод на русский:*\n\n"

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

# Render-da barqaror ishlashi uchun tuzatilgan ishga tushirish qismi
if __name__ == "__main__":
    # Botni alohida oqimda (Thread) xavfsiz ishga tushiramiz
    threading.Thread(target=bot.infinity_polling, kwargs={"skip_pending": True}).start()
    
    # Flask portini Render muhitidan olamiz
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
