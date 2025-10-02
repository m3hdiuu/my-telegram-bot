from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import pandas as pd
import os
import locale
import utils
from datetime import datetime, time
import jdatetime

# تنظیم locale برای جدا کردن اعداد
locale.setlocale(locale.LC_ALL, 'fa_IR.UTF-8')

def escape_markdown(text):
    """اسکیپ کاراکترهای خاص برای MarkdownV2"""
    escape_chars = r'!\.\-'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def calculate_days_left(end_date_str, submission_deadline=None):
    """محاسبه روزهای باقی‌مانده تا مهلت دریافت اسناد یا مهلت تمدید شده"""
    if end_date_str == "نامشخص" and (submission_deadline is None or submission_deadline == "نامشخص"):
        return "نامشخص"
    try:
        if submission_deadline and submission_deadline != "نامشخص":
            end_date_obj = jdatetime.datetime.strptime(submission_deadline, "%Y/%m/%d").replace(hour=23, minute=59, second=59).togregorian()
        else:
            end_date_obj = jdatetime.datetime.strptime(end_date_str, "%Y/%m/%d").replace(hour=23, minute=59, second=59).togregorian()
        today = jdatetime.datetime.now()
        days_left = (end_date_obj - today).days
        if days_left < 0:
            return "مهلت به پایان رسیده است ⏰"
        elif days_left == 0:
            return "آخرین روز مهلت 🌱"
        return f"{days_left} روز باقی مانده 🌱"
    except ValueError:
        return "فرمت تاریخ نامعتبر 📅"

def show_tenders(update: Update, context: CallbackContext, page: int = 0) -> None:
    query = update.callback_query
    if context.user_data.get('last_message_id'):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
        except Exception as e:
            print(f"Error deleting message: {e}")

    try:
        df = pd.read_excel('tenders.xlsx')
        print(f"Debug: Total items = {len(df)}, Page = {page}")  # دیباگ
        if df.empty:
            tender_info = escape_markdown("لیست مناقصه‌ها خالی است\\. لطفاً با ادمین تماس بگیرید\\.")
            keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = query.message.reply_text(tender_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
            context.user_data['last_message_id'] = message.message_id
            return

        items_per_page = 3
        total_items = len(df)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        print(f"Debug: Total pages = {total_pages}")  # دیباگ
        start_idx = page * items_per_page
        end_idx = min((page + 1) * items_per_page, total_items)

        for index in range(start_idx, end_idx):
            row = df.iloc[index]
            tender_id = row['id']
            tender_title = row['title']
            description = row['description'] or "بدون توضیحات"
            estimated_amount = row['estimated_amount'] or 0
            contract_duration = row['contract_duration'] or "نامشخص"
            start_date = row['start_date'] or "نامشخص"
            end_date = row['end_date'] or "نامشخص"
            evaluation_start = row['evaluation_start'] or "نامشخص"
            contractor_rank = row['contractor_rank'] or "نامشخص"
            tender_guarantee = row['tender_guarantee'] or 0
            renewal_count = row.get('renewal_count', 0)
            submission_deadline = row.get('submission_deadline', None) or "نامشخص"
            # جدا کردن سه‌رقمی برای مبلغ برآورد و تضمین
            formatted_amount = locale.format_string("%d", int(estimated_amount), grouping=True) + " ریال" if estimated_amount else "نامشخص"
            formatted_guarantee = locale.format_string("%d", int(tender_guarantee), grouping=True) + " ریال" if tender_guarantee else "نامشخص"
            tender_info = (
                f"🎯 <b>عنوان</b>: {escape_markdown(tender_title)}\n"
                f"📝 <b>توضیحات</b>: {escape_markdown(description)}\n"
                f"💰 <b>مبلغ</b>: {formatted_amount}\n"
                f"⏳ <b>مدت</b>: {contract_duration}\n"
                f"🏆 <b>رتبه</b>: {contractor_rank}\n"
                f"🔒 <b>تضمین</b>: {formatted_guarantee}\n"
                f"📅 <b>شروع</b>: {start_date}\n"
            )
            # نمایش اطلاعات با خط خوردگی اگه تجدید شده باشه
            if renewal_count > 0:
                tender_info += f'⏰ <b>مهلت دریافت اسناد</b>: <s>{end_date}</s>\n'
                if pd.notna(submission_deadline) and submission_deadline != "نامشخص":
                    tender_info += f'📅 <b>مهلت تجدید شده دریافت اسناد</b>: {submission_deadline}\n'
                tender_info += f'🔍 <b>ارزیابی</b>: <s>{evaluation_start}</s>\n'
                if pd.notna(row['opening_date']):
                    tender_info += f'📅 <b>مهلت تجدید شده بازگشایی اسناد</b>: {row["opening_date"]}\n'
                tender_info += f'<span class="tg-spoiler">🔄 تجدید {renewal_count} بار</span>'
            else:
                tender_info += f'⏰ <b>مهلت دریافت اسناد</b>: {end_date}\n'
                tender_info += f'🔍 <b>ارزیابی</b>: {evaluation_start}\n'

            # اضافه کردن روزهای باقی‌مانده
            days_left = calculate_days_left(end_date, submission_deadline if pd.notna(submission_deadline) else None)
            tender_info += f"\n⏳ <b>زمان باقی‌مانده</b>: {days_left}"

            # چک کردن مهلت برای نمایش دکمه‌ها
            keyboard = []
            if days_left not in ["مهلت به پایان رسیده است ⏰", "نامشخص", "فرمت تاریخ نامعتبر 📅"]:
                keyboard = [
                    [InlineKeyboardButton("دانلود اسناد ارزیابی", callback_data=f'download_{tender_id}'),
                     InlineKeyboardButton("آگهی فراخوان ارزیابی", callback_data=f'more_details_{tender_id}')]
                ]

            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else InlineKeyboardMarkup([])
            message = query.message.reply_text(tender_info, reply_markup=reply_markup, parse_mode='HTML')
            context.user_data['last_message_id'] = message.message_id

        # دکمه‌های صفحه‌بندی
        keyboard_back = []
        if page > 0:
            keyboard_back.append(InlineKeyboardButton("⏪", callback_data=f'tenders_page_{page - 1}'))
        if page < total_pages - 1:
            keyboard_back.append(InlineKeyboardButton("⏩", callback_data=f'tenders_page_{page + 1}'))
        keyboard_back.append(InlineKeyboardButton("🏠", callback_data='main_menu'))  # بازگشت به صفحه اصلی
        if keyboard_back:
            reply_markup_back = InlineKeyboardMarkup([keyboard_back])
            message_back = query.message.reply_text("ادامه لیست", reply_markup=reply_markup_back, parse_mode='MarkdownV2')
            context.user_data['last_message_id'] = message_back.message_id
        else:
            keyboard_back = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
            reply_markup_back = InlineKeyboardMarkup(keyboard_back)
            message_back = query.message.reply_text("بازگشت", reply_markup=reply_markup_back, parse_mode='MarkdownV2')
            context.user_data['last_message_id'] = message_back.message_id

    except FileNotFoundError:
        tender_info = escape_markdown("فایل مناقصه‌ها \\(tenders\\.xlsx\\) یافت نشد\\. لطفاً با ادمین تماس بگیرید\\.")
        keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(tender_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id
    except Exception as e:
        safe_error = escape_markdown(str(e).replace('.', '\.').replace('-', '\-'))
        tender_info = f"خطا: {safe_error}\\. لطفاً با ادمین تماس بگیرید\\."
        keyboard = [[InlineKeyboardButton("🔙", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = query.message.reply_text(tender_info, reply_markup=reply_markup, parse_mode='MarkdownV2')
        context.user_data['last_message_id'] = message.message_id

def send_document(update: Update, context: CallbackContext, tender_id: str) -> None:
    query = update.callback_query
    document_path = f"/home/alireza4083/documents/tender_{tender_id}.pdf"
    if os.path.exists(document_path):
        with open(document_path, 'rb') as document:
            query.message.reply_document(document, caption=f"اسناد {tender_id}", parse_mode='MarkdownV2')
        stats = utils.load_stats()
        user_id = update.effective_user.id
        stats["downloads"][str(user_id)] = stats["downloads"].get(str(user_id), set()).union({tender_id})
        stats["tender_downloads"][tender_id] = stats["tender_downloads"].get(tender_id, 0) + 1
        utils.save_stats(stats)
    else:
        query.message.reply_text("📝 اسناد یافت نشد\\.", parse_mode='MarkdownV2')
    keyboard = [
        [InlineKeyboardButton("⏪", callback_data='tenders_page_0')],
        [InlineKeyboardButton("🏠", callback_data='main_menu')],
        [InlineKeyboardButton("⏩", callback_data='tenders_page_0')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(" ", reply_markup=reply_markup, parse_mode='MarkdownV2')
    context.user_data['last_message_id'] = message.message_id
    query.answer()

def show_more_details(update: Update, context: CallbackContext, tender_id: str) -> None:
    query = update.callback_query
    # مسیر فایل JPG برای جزئیات مناقصه
    details_path = f"/home/alireza4083/documents/details_{tender_id}.jpg"

    # چک کردن وجود فایل
    if os.path.exists(details_path):
        with open(details_path, 'rb') as photo:
            query.message.reply_photo(
                photo=photo,
                caption=f"آگهی ارزیابی  {tender_id}",
                parse_mode='MarkdownV2'
            )
    else:
        query.message.reply_text(
            f"تصویر آگهی ارزیابی برای مناقصه {tender_id} یافت نشد\\.",
            parse_mode='MarkdownV2'
        )

    # دکمه‌های بازگشت
    keyboard = [
        [InlineKeyboardButton("⏪", callback_data='tenders_page_0')],
        [InlineKeyboardButton("🏠", callback_data='main_menu')],
        [InlineKeyboardButton("⏩", callback_data='tenders_page_0')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = query.message.reply_text(" ", reply_markup=reply_markup, parse_mode='MarkdownV2')
    context.user_data['last_message_id'] = message.message_id
    query.answer()

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
    message = query.message.reply_text(" ", reply_markup=reply_markup, parse_mode='MarkdownV2')
    context.user_data['last_message_id'] = message.message_id
    query.answer()