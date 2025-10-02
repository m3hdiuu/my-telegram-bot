from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os
import utils

def load_internal_numbers():
    numbers_file = 'internal_numbers.txt'
    if os.path.exists(numbers_file):
        with open(numbers_file, 'r', encoding='utf-8') as file:
            return '\n'.join([line.strip() for line in file if line.strip()])
    return "فایل شماره‌های داخلی یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."

def show_contact_us(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_message_id'])
        except:
            pass

    try:
        with open('contact_us.txt', 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        content = "فایل تماس یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."

    content += "\n\n🏠 <b>آدرس</b>: نیشابور - بلوار معلم - معلم 9 - پلاک 18\n📮 <b>کد پستی</b>: 12345679\n🌐 <b>موقعیت</b>: https://maps.google.com/?q=36.2087,58.7969"

    keyboard = [
        [InlineKeyboardButton("🏠", callback_data='main_menu'),
         InlineKeyboardButton("📞 تلفن‌های داخلی", callback_data='show_internal_numbers')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(content, reply_markup=reply_markup, parse_mode='HTML')
    context.user_data['last_message_id'] = message.message_id
    query.answer()

def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'show_internal_numbers':
        internal_numbers = load_internal_numbers()
        # ارسال پیام جدید به‌جای ویرایش
        keyboard = [
            [InlineKeyboardButton("🏠 بازگشت", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"<b>📞 شماره‌های داخلی:</b>\n{internal_numbers}",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )