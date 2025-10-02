# rev 8 date: 1404-06-15 Time 10:30am
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import pandas as pd
import os
import json
import shutil
import schedule
import time
import utils
import config
import matplotlib
matplotlib.use('Agg')  # برای استفاده در سرور بدون GUI
import matplotlib.pyplot as plt
from io import BytesIO

def show_admin_dashboard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    stats = utils.load_stats()
    total_users = len(stats["users"])
    total_downloads = sum(stats["tender_downloads"].values())
    tender_download_details = "\n".join([f"مناقصه {tender}: {count}" for tender, count in stats["tender_downloads"].items()]) or "بدون دانلود"

    # ایجاد نمودار
    plt.figure(figsize=(10, 5))
    tenders = list(stats["tender_downloads"].keys())
    downloads = list(stats["tender_downloads"].values())
    plt.bar(tenders, downloads, color='skyblue')
    plt.title("دانلودها")
    plt.xlabel("مناقصه")
    plt.ylabel("تعداد")
    plt.xticks(rotation=45)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    query.message.reply_photo(photo=buf, caption="📊 نمودار", parse_mode='MarkdownV2')
    dashboard_text = (
        f"📊 <b>داشبورد</b>\n"
        f"کاربران: {total_users}\n"
        f"دانلودها: {total_downloads}\n"
        f"جزئیات:\n{tender_download_details}"
    )
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت مناقصه‌ها", callback_data='manage_tenders')],
        [InlineKeyboardButton("🏠", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(dashboard_text, reply_markup=reply_markup, parse_mode='HTML')
    context.user_data['last_message_id'] = message.message_id
    buf.close()

def manage_tenders(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    df = pd.read_excel('tenders.xlsx')
    keyboard = []
    for index, row in df.iterrows():
        tender_id = row['id']
        tender_title = row['title']
        keyboard.append([InlineKeyboardButton(f"{tender_title} (ID: {tender_id})", callback_data=f'renew_tender_{tender_id}')])
    keyboard.append([InlineKeyboardButton("➕ افزودن مناقصه", callback_data='add_tender')])
    keyboard.append([InlineKeyboardButton("🏠", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text("مدیریت مناقصه‌ها", reply_markup=reply_markup, parse_mode='MarkdownV2')
    context.user_data['last_message_id'] = message.message_id
    query.answer()

def add_tender(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.message.reply_text("لطفاً اطلاعات مناقصه (عنوان، توضیحات، ...) را ارسال کنید.", parse_mode='MarkdownV2')
    context.user_data['state'] = 'adding_tender'
    context.user_data['last_message_id'] = query.message.message_id
    query.answer()

def handle_admin_input(update: Update, context: CallbackContext, text: str) -> None:
    user_id = update.effective_user.id
    if user_id not in utils.load_admins():
        return
    if context.user_data.get('state') == 'adding_tender':
        # اینجا منطق افزودن مناقصه رو می‌تونی پیاده‌سازی کنی (مثلاً با پارسر متن)
        update.message.reply_text("مناقصه با موفقیت اضافه شد! (در حال توسعه)", parse_mode='MarkdownV2')
        context.user_data.pop('state', None)
    else:
        update.message.reply_text("دستور نامعتبر\\. لطفاً از منوی ادمین استفاده کنید\\.", parse_mode='MarkdownV2')

def renew_tender(update: Update, context: CallbackContext, tender_id: str) -> None:
    query = update.callback_query
    df = pd.read_excel('tenders.xlsx')
    row = df[df['id'] == tender_id].iloc[0]
    if pd.isna(row['end_date']) or pd.isna(row['submission_deadline']) or pd.isna(row['opening_date']):
        query.message.reply_text("تاریخ‌های مناقصه ناقص است\\. لطفاً ابتدا تکمیل کنید\\.", parse_mode='MarkdownV2')
        return

    # افزایش 7 روز به تاریخ‌ها
    days_to_add = 7
    end_date = jdatetime.datetime.strptime(row['end_date'], "%Y/%m/%d").togregorian()
    submission_deadline = jdatetime.datetime.strptime(row['submission_deadline'], "%Y/%m/%d").togregorian()
    opening_date = jdatetime.datetime.strptime(row['opening_date'], "%Y/%m/%d").togregorian()

    new_end_date = end_date + datetime.timedelta(days=days_to_add)
    new_submission_deadline = submission_deadline + datetime.timedelta(days=days_to_add)
    new_opening_date = opening_date + datetime.timedelta(days=days_to_add)

    # تبدیل به فرمت شمسی
    new_end_date_str = jdatetime.GregorianToJalali(new_end_date.year, new_end_date.month, new_end_date.day).strftime("%Y/%m/%d")
    new_submission_deadline_str = jdatetime.GregorianToJalali(new_submission_deadline.year, new_submission_deadline.month, new_submission_deadline.day).strftime("%Y/%m/%d")
    new_opening_date_str = jdatetime.GregorianToJalali(new_opening_date.year, new_opening_date.month, new_opening_date.day).strftime("%Y/%m/%d")

    # به‌روزرسانی داده‌ها
    df.loc[df['id'] == tender_id, 'end_date'] = new_end_date_str
    df.loc[df['id'] == tender_id, 'submission_deadline'] = new_submission_deadline_str
    df.loc[df['id'] == tender_id, 'opening_date'] = new_opening_date_str
    df.loc[df['id'] == tender_id, 'renewal_count'] = row.get('renewal_count', 0) + 1

    # ذخیره تغییرات
    df.to_excel('tenders.xlsx', index=False)
    query.message.reply_text(f"مناقصه {tender_id} تجدید شد\\. مهلت‌ها 7 روز افزایش یافت:\n- مهلت دریافت اسناد: {new_end_date_str}\n- مهلت ارسال اسناد: {new_submission_deadline_str}\n- بازگشایی پاکت: {new_opening_date_str}", parse_mode='MarkdownV2')
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت مناقصه‌ها", callback_data='manage_tenders')],
        [InlineKeyboardButton("🏠", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text("", reply_markup=reply_markup, parse_mode='MarkdownV2')
    context.user_data['last_message_id'] = message.message_id
    query.answer()

def run_scheduler(updater):
    schedule.every().day.at("00:00").do(lambda: None)
    while True:
        schedule.run_pending()
        time.sleep(60)