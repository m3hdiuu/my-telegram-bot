# rev 8 date: 1404-06-15 Time 04:20pm
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os

def show_about_us(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_message_id'])
        except:
            pass

    try:
        with open('about_us.txt', 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        content = "فایل درباره ما یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."

    keyboard = [
        [InlineKeyboardButton("👥 اعضای هیئت", callback_data='board_members')],
        [InlineKeyboardButton("📊 چارت", callback_data='org_chart')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(content, reply_markup=reply_markup, parse_mode='HTML')
    context.user_data['last_message_id'] = message.message_id
    query.answer()

def show_board_members(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_message_id'])
        except:
            pass

    try:
        with open('board_members.txt', 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        content = "فایل اعضای هیئت مدیره یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."

    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data='about_us')],
        [InlineKeyboardButton("🏠", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(content, reply_markup=reply_markup, parse_mode='HTML')
    context.user_data['last_message_id'] = message.message_id
    query.answer()

def show_org_chart(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_message_id'])
        except:
            pass

    chart_path = 'org_chart.jpg'
    if os.path.exists(chart_path):
        with open(chart_path, 'rb') as chart:
            query.message.reply_photo(photo=chart, caption="<b>چارت سازمانی</b>", parse_mode='HTML')
    else:
        query.message.reply_text("فایل چارت یافت نشد\\. لطفاً با ادمین تماس بگیرید\\.", parse_mode='MarkdownV2')

    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data='about_us')],
        [InlineKeyboardButton("🏠", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text("", reply_markup=reply_markup, parse_mode='MarkdownV2')
    context.user_data['last_message_id'] = message.message_id
    query.answer()

def show_internal_phones(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_message_id'])
        except:
            pass

    try:
        with open('internal_phones.txt', 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        content = "فایل تلفن‌ها یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."

    keyboard = [
        [InlineKeyboardButton("🏠", callback_data='main_menu')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='about_us')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(content, reply_markup=reply_markup, parse_mode='HTML')
    context.user_data['last_message_id'] = message.message_id
    query.answer()