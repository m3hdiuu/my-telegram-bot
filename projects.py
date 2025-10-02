# rev 3 date: 1404-06-15 Time 17:25pm
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import pandas as pd
import os

def handle_projects(update: Update, context: CallbackContext, page: int = 0) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
        except Exception as e:
            print(f"Error deleting message: {e}")

    try:
        # فرض بر اینه که پروژه‌ها توی فایل projects.xlsx ذخیره شده
        df = pd.read_excel('projects.xlsx')
        print(f"Debug: Available columns = {df.columns.tolist()}")  # دیباگ برای چک کردن ستون‌ها
        if df.empty:
            project_info = "📸 **لیست پروژه‌ها خالی است**. لطفاً با ادمین تماس بگیرید."
            keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = query.message.reply_text(project_info, reply_markup=reply_markup, parse_mode='Markdown')
            context.user_data['last_message_id'] = message.message_id
            return

        items_per_page = 3
        total_items = len(df)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        start_idx = page * items_per_page
        end_idx = min((page + 1) * items_per_page, total_items)

        for index in range(start_idx, end_idx):
            row = df.iloc[index]
            project_id = row.get('id', 'بدون شناسه')
            project_title = row.get('title', 'بدون عنوان')
            description = row.get('description', 'بدون توضیحات')  # مقدار پیش‌فرض اگه ستون وجود نداشته باشه
            project_info = f"📌 **عنوان پروژه**: {project_title}\n📝 **توضیحات**: {description}"

            keyboard = [
                [InlineKeyboardButton("ℹ️ جزئیات", callback_data=f'project_{project_id}')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = query.message.reply_text(project_info, reply_markup=reply_markup, parse_mode='Markdown')
            context.user_data['last_message_id'] = message.message_id

        # دکمه‌های صفحه‌بندی
        keyboard_back = []
        if page > 0:
            keyboard_back.append(InlineKeyboardButton("⏪", callback_data=f'projects_page_{page - 1}'))
        if page < total_pages - 1:
            keyboard_back.append(InlineKeyboardButton("⏩", callback_data=f'projects_page_{page + 1}'))
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

    except FileNotFoundError:
        project_info = "فایل پروژه‌ها (projects.xlsx) یافت نشد\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(project_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id
    except Exception as e:
        print(f"Error in handle_projects: {e}")  # دیباگ دقیق‌تر
        project_info = f"خطا: {str(e)}\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(project_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id

def show_project_details(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
        except Exception as e:
            print(f"Error deleting message: {e}")

    project_id = query.data.replace('project_', '')
    project_info = f"ℹ️ **جزئیات پروژه {project_id}**\nجزئیات هنوز در دسترس نیست. به زودی تکمیل می‌شود."
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data='projects_page_0')],
        [InlineKeyboardButton("🏠", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(project_info, reply_markup=reply_markup, parse_mode='Markdown')
    context.user_data['last_message_id'] = message.message_id
    query.answer()