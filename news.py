# rev 12 date: 1404-06-17 Time 01:50am
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import pandas as pd
import os

def show_news(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
        except Exception as e:
            print(f"Error deleting message: {e}")

    try:
        df = pd.read_excel('news.xlsx')
        print(f"Debug: Total items = {len(df)}, Columns = {df.columns.tolist()}")  # دیباگ
        if df.empty:
            news_info = "📰 **لیست اخبار خالی است**. لطفاً با ادمین تماس بگیرید\\."
            keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = query.message.reply_text(news_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
            context.user_data['last_message_id'] = message.message_id
            return

        # مرتب‌سازی بر اساس تاریخ و ساعت (جدیدترین اول)
        df = df.sort_values(by=['date', 'time'], ascending=[False, False])

        page = context.user_data.get('news_page', 0)
        items_per_page = 3
        total_items = len(df)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        start_idx = page * items_per_page
        end_idx = min((page + 1) * items_per_page, total_items)

        for index in range(start_idx, end_idx):
            row = df.iloc[index]
            news_id = str(row.get('id', 'بدون شناسه'))  # تبدیل به رشته برای تطابق بهتر
            news_title = row.get('title', 'بدون عنوان')
            short_text = row.get('short_text', 'بدون خلاصه')
            news_info = f"📰 **{news_title}**\n📝 **خلاصه**: {short_text}"

            keyboard = [
                [InlineKeyboardButton("مشروح خبر", callback_data=f'full_news_{news_id}')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = query.message.reply_text(news_info, reply_markup=reply_markup, parse_mode='Markdown')
            context.user_data['last_message_id'] = message.message_id

        # دکمه‌های صفحه‌بندی
        keyboard_back = []
        if page > 0:
            keyboard_back.append(InlineKeyboardButton("⏪", callback_data='news_page_prev'))
        if page < total_pages - 1:
            keyboard_back.append(InlineKeyboardButton("⏩", callback_data='news_page_next'))
        keyboard_back.append(InlineKeyboardButton("🏠", callback_data='main_menu'))  # بازگشت به صفحه اصلی
        if keyboard_back:
            reply_markup_back = InlineKeyboardMarkup([keyboard_back])
            message_back = query.message.reply_text("ادامه لیست", reply_markup=reply_markup_back, parse_mode='Markdown')
            context.user_data['last_message_id'] = message_back.message_id
        else:
            keyboard_back = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
            reply_markup_back = InlineKeyboardMarkup(keyboard_back)
            message_back = query.message.reply_text("بازگشت", reply_markup=reply_markup_back, parse_mode='Markdown')
            context.user_data['last_message_id'] = message_back.message_id

        context.user_data['news_page'] = page

    except FileNotFoundError:
        news_info = "فایل اخبار \\(news\\.xlsx\\) یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(news_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id
    except Exception as e:
        print(f"Error in show_news: {e}")
        news_info = f"خطا: {str(e)}\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(news_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id

def show_full_news(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    # حذف همه پیام‌های قبلی
    if 'message_ids' in context.user_data:
        for msg_id in context.user_data['message_ids']:
            try:
                context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
            except Exception as e:
                print(f"Debug: Failed to delete message {msg_id}: {e}")
        del context.user_data['message_ids']
    else:
        if context.user_data.get('last_message_id'):
            try:
                context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
            except Exception as e:
                print(f"Debug: Failed to delete message {context.user_data['last_message_id']}: {e}")

    news_id = query.data.replace('full_news_', '')
    try:
        df = pd.read_excel('news.xlsx')
        print(f"Debug: Searching for news_id = {news_id}, Columns = {df.columns.tolist()}, id type = {df['id'].dtype}")
        # تطابق id با نوع داده (عدد یا رشته)
        if df['id'].dtype == float or df['id'].dtype == int:
            news_id_num = float(news_id) if news_id.isdigit() else None
            if news_id_num is not None:
                row = df[df['id'] == news_id_num].iloc[0]
            else:
                raise ValueError("news_id is not a valid number")
        else:
            row = df[df['id'] == news_id].iloc[0]
        news_title = row.get('title', 'بدون عنوان')
        full_text = row.get('full_text', 'متن کامل خبر در دسترس نیست.')
        news_date = row.get('date', 'بدون تاریخ')
        news_time = row.get('time', 'بدون ساعت')
        news_info = f"📰 **{news_title}**\n\n📖 **متن کامل**: {full_text}\n\n📅 **تاریخ**: {news_date}\n⏰ **ساعت**: {news_time}"
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت", callback_data='news')],
            [InlineKeyboardButton("🏠", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(news_info, reply_markup=reply_markup, parse_mode='Markdown')
        context.user_data['last_message_id'] = message.message_id
        if 'message_ids' not in context.user_data:
            context.user_data['message_ids'] = []
        context.user_data['message_ids'].append(message.message_id)
    except (IndexError, ValueError) as e:
        print(f"Debug: Error in show_full_news: {e}, Dataframe shape = {df.shape}, id match = {len(df[df['id'] == (float(news_id) if news_id.isdigit() else news_id)])}")
        news_info = "خطا: خبری با این شناسه یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت", callback_data='news')],
            [InlineKeyboardButton("🏠", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(news_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id
        if 'message_ids' not in context.user_data:
            context.user_data['message_ids'] = []
        context.user_data['message_ids'].append(message.message_id)
    except Exception as e:
        print(f"Error in show_full_news: {e}")
        news_info = "خطا در بارگذاری متن کامل خبر\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت", callback_data='news')],
            [InlineKeyboardButton("🏠", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(news_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id
        if 'message_ids' not in context.user_data:
            context.user_data['message_ids'] = []
        context.user_data['message_ids'].append(message.message_id)
    query.answer()

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'news':
        show_news(update, context)
    elif query.data == 'news_page_prev':
        context.user_data['news_page'] = max(0, context.user_data.get('news_page', 0) - 1)
        show_news(update, context)
    elif query.data == 'news_page_next':
        context.user_data['news_page'] = context.user_data.get('news_page', 0) + 1
        show_news(update, context)
    elif query.data.startswith('full_news_'):
        show_full_news(update, context)
    query.answer()