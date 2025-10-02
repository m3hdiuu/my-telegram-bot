# rev 7 date: 1404-06-13 Time 09:15am
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, CommandHandler
import utils
import pandas as pd
import os

# حالت‌های مکالمه
NAME, EMAIL, PHONE, RESUME = range(4)

def start_registration(update: Update, context: CallbackContext) -> int:
    print("Entering start_registration")  # دیباگ
    query = update.callback_query
    if query:
        query.answer()  # تأیید دریافت callback
        context.user_data['supplier_type'] = 'پیمانکار'  # فرض نقش "پیمانکار"
        print("Role set to پیمانکار")  # دیباگ
        query.message.reply_text("لطفاً نام شرکت یا نام خود را وارد کنید:", parse_mode='Markdown')
        return NAME
    return ConversationHandler.END  # اگه query نباشه، فرآیند تموم می‌شه

def name(update: Update, context: CallbackContext) -> int:
    print("Entering name")  # دیباگ
    if update.message:
        context.user_data['name'] = update.message.text
        print(f"Name received: {update.message.text}")  # دیباگ
        update.message.reply_text("لطفاً ایمیل خود را وارد کنید:", parse_mode='Markdown')
        return EMAIL
    return NAME  # اگه پیام نباشه، به حالت فعلی بمون

def email(update: Update, context: CallbackContext) -> int:
    print("Entering email")  # دیباگ
    if update.message:
        context.user_data['email'] = update.message.text
        print(f"Email received: {update.message.text}")  # دیباگ
        update.message.reply_text("لطفاً شماره تماس خود را وارد کنید:", parse_mode='Markdown')
        return PHONE
    return EMAIL  # اگه پیام نباشه، به حالت فعلی بمون

def phone(update: Update, context: CallbackContext) -> int:
    print("Entering phone")  # دیباگ
    if update.message:
        context.user_data['phone'] = update.message.text
        print(f"Phone received: {update.message.text}")  # دیباگ
        update.message.reply_text("لطفاً رزومه خود را به صورت PDF (حداکثر 5 مگابایت) آپلود کنید:", parse_mode='Markdown')
        return RESUME
    return PHONE  # اگه پیام نباشه، به حالت فعلی بمون

def resume(update: Update, context: CallbackContext) -> int:
    print("Entering resume")  # دیباگ
    if update.message.document:
        file = update.message.document
        if file.file_size > 5 * 1024 * 1024:
            update.message.reply_text("فایل رزومه بیش از 5 مگابایت است. لطفاً فایل کوچک‌تری آپلود کنید.", parse_mode='Markdown')
            return RESUME
        if file.mime_type != "application/pdf":
            update.message.reply_text("لطفاً فقط فایل PDF آپلود کنید.", parse_mode='Markdown')
            return RESUME
        file_id = file.file_id
        os.makedirs("resumes", exist_ok=True)
        file_path = f"resumes/resume_{update.effective_user.id}_{utils.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        context.bot.get_file(file_id).download(file_path)
        context.user_data['resume'] = file_path
    else:
        update.message.reply_text("لطفاً یک فایل PDF آپلود کنید.", parse_mode='Markdown')
        return RESUME

    # ذخیره اطلاعات
    supplier_data = {
        'user_id': update.effective_user.id,
        'supplier_type': context.user_data['supplier_type'],
        'name': context.user_data['name'],
        'email': context.user_data['email'],
        'phone': context.user_data['phone'],
        'resume': context.user_data['resume'],
        'timestamp': utils.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    suppliers = utils.load_suppliers()
    suppliers.append(supplier_data)
    utils.save_suppliers(suppliers)

    # ذخیره در اکسل
    df = pd.read_excel('suppliers.xlsx') if os.path.exists('suppliers.xlsx') else pd.DataFrame(columns=['user_id', 'supplier_type', 'name', 'email', 'phone', 'resume', 'timestamp'])
    df = pd.concat([df, pd.DataFrame([supplier_data])], ignore_index=True)
    df.to_excel('suppliers.xlsx', index=False)

    update.message.reply_text(
        "**ثبت‌نام شما با موفقیت انجام شد. به زودی با شما تماس گرفته خواهد شد.**\nبرای بازگشت به منوی اصلی، /start را بزنید.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='main_menu')]])
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    print("Entering cancel")  # دیباگ
    update.message.reply_text("ثبت‌نام لغو شد. برای بازگشت به منوی اصلی، /start را بزنید.", parse_mode='Markdown')
    return ConversationHandler.END

def registration_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_registration, pattern='^supplier_registration$')],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone)],
            RESUME: [MessageHandler(Filters.document, resume)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )