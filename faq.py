# rev 3 date: 1404-06-17 Time 01:30am
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import pandas as pd
import os

def show_faq(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
        except Exception as e:
            print(f"Debug: Failed to delete message: {e}")

    try:
        df = pd.read_excel('faq.xlsx')
        print(f"Debug: Total items = {len(df)}, Columns = {df.columns.tolist()}")  # دیباگ
        if df.empty:
            faq_info = "❓ **لیست سؤالات متداول خالی است**. لطفاً با ادمین تماس بگیرید\\."
            keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = query.message.reply_text(faq_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
            context.user_data['last_message_id'] = message.message_id
            return

        page = context.user_data.get('faq_page', 0)
        items_per_page = 3
        total_items = len(df)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        start_idx = page * items_per_page
        end_idx = min((page + 1) * items_per_page, total_items)

        faq_text = "❓ **سؤالات متداول**\n\n"
        for index in range(start_idx, end_idx):
            row = df.iloc[index]
            question = row.get('question', 'بدون سؤال')
            answer = row.get('answer', 'بدون پاسخ')
            faq_text += f"**سؤال:** {question}\n**جواب:** {answer}\n\n"

        keyboard_back = []
        if page > 0:
            keyboard_back.append(InlineKeyboardButton("⏪ صفحه قبل", callback_data='faq_page_prev'))
        if page < total_pages - 1:
            keyboard_back.append(InlineKeyboardButton("⏩ صفحه بعد", callback_data='faq_page_next'))
        keyboard_back.append(InlineKeyboardButton("🏠 خانه", callback_data='main_menu'))
        reply_markup = InlineKeyboardMarkup([keyboard_back])
        message = query.message.reply_text(faq_text, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id

        context.user_data['faq_page'] = page

    except FileNotFoundError:
        faq_info = "فایل FAQ (faq\\.xlsx) یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(faq_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id
    except Exception as e:
        print(f"Error in show_faq: {e}")
        faq_info = f"خطا: {str(e)}\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(faq_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'faq':
        show_faq(update, context)
    elif query.data == 'faq_page_prev':
        context.user_data['faq_page'] = max(0, context.user_data.get('faq_page', 0) - 1)
        show_faq(update, context)
    elif query.data == 'faq_page_next':
        context.user_data['faq_page'] = context.user_data.get('faq_page', 0) + 1
        show_faq(update, context)
    query.answer()