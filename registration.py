# rev 2 date: 1404-06-17 Time 01:20am
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
import pandas as pd
import os
from datetime import datetime

(NAME, CONTACT, TYPE) = range(3)

def start_registration(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
        except Exception as e:
            print(f"Debug: Failed to delete message: {e}")

    reg_info = "📝 **ثبت‌نام تأمین‌کنندگان، پیمانکاران و مشاوران**\nلطفاً نام خود یا شرکت را وارد کنید:"
    message = query.message.reply_text(reg_info, parse_mode='Markdown')
    context.user_data['last_message_id'] = message.message_id
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['name'] = update.message.text
    reg_info = f"👤 نام شما: {context.user_data['name']}\nلطفاً شماره تماس خود را وارد کنید:"
    update.message.reply_text(reg_info, parse_mode='Markdown')  # استفاده از update.message به‌جای reply_text جداگانه
    return CONTACT

def get_contact(update: Update, context: CallbackContext) -> int:
    context.user_data['contact'] = update.message.text
    reg_info = f"📞 شماره تماس شما: {context.user_data['contact']}\nلطفاً نوع فعالیت (تأمین‌کننده، پیمانکار یا مشاور) را وارد کنید:"
    update.message.reply_text(reg_info, parse_mode='Markdown')
    return TYPE

def get_type(update: Update, context: CallbackContext) -> int:
    context.user_data['type'] = update.message.text
    reg_info = (f"✅ **ثبت‌نام تکمیل شد**\n"
                f"نام: {context.user_data['name']}\n"
                f"شماره تماس: {context.user_data['contact']}\n"
                f"نوع فعالیت: {context.user_data['type']}\n"
                f"تاریخ ثبت: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    keyboard = [[InlineKeyboardButton("🏠", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(reg_info, reply_markup=reply_markup, parse_mode='Markdown')

    # ذخیره اطلاعات توی فایل
    if os.path.exists('registrations.xlsx'):
        df = pd.read_excel('registrations.xlsx')
    else:
        df = pd.DataFrame(columns=['name', 'contact', 'type', 'date'])
    new_row = pd.DataFrame([{
        'name': context.user_data['name'],
        'contact': context.user_data['contact'],
        'type': context.user_data['type'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel('registrations.xlsx', index=False)

    return ConversationHandler.END

def cancel_registration(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
        except Exception as e:
            print(f"Debug: Failed to delete message: {e}")
    update.message.reply_text("❌ ثبت‌نام لغو شد.", parse_mode='Markdown')
    return ConversationHandler.END

def registration_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
        except Exception as e:
            print(f"Debug: Failed to delete message: {e}")
    reg_info = "📝 **ثبت‌نام تأمین‌کنندگان، پیمانکاران و مشاوران**\nبرای شروع ثبت‌نام، دکمه زیر را فشار دهید:"
    keyboard = [[InlineKeyboardButton("شروع ثبت‌نام", callback_data='start_registration')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(reg_info, reply_markup=reply_markup, parse_mode='Markdown')
    context.user_data['last_message_id'] = message.message_id

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_registration, pattern='^start_registration$')],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        CONTACT: [MessageHandler(Filters.text & ~Filters.command, get_contact)],
        TYPE: [MessageHandler(Filters.text & ~Filters.command, get_type)],
    },
    fallbacks=[CallbackQueryHandler(cancel_registration, pattern='^cancel$')]
)