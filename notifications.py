# rev 1 date: 1404-06-13 Time 12:30am
from telegram.ext import CallbackContext
import pandas as pd
import os
import schedule
import time
import jdatetime
import utils
import config

def check_tender_deadlines(context: CallbackContext) -> None:
    try:
        df = pd.read_excel('tenders.xlsx')
        today = jdatetime.datetime.now().togregorian()
        for index, row in df.iterrows():
            end_date = row['end_date']
            tender_id = row['id']
            if end_date and end_date != "نامشخص":
                end_date_obj = jdatetime.datetime.strptime(end_date, "%Y/%m/%d").togregorian()
                days_left = (end_date_obj - today).days
                if 0 < days_left <= 2:
                    message = (
                        f"⚠️ **هشدار مهلت مناقصه**\n"
                        f"مناقصه {row['title']} (ID: {tender_id}) در {days_left} روز دیگر منقضی می‌شود.\n"
                        f"مهلت: {end_date}"
                    )
                    context.bot.send_message(chat_id=config.ADMIN_ID, text=message, parse_mode='MarkdownV2')
    except Exception as e:
        context.bot.send_message(chat_id=config.ADMIN_ID, text=f"خطا در چک کردن مهلت‌ها: {str(e)}", parse_mode='MarkdownV2')

def run_notifications(updater):
    schedule.every().day.at("09:00").do(check_tender_deadlines, context=updater.job_queue)
    while True:
        schedule.run_pending()
        time.sleep(60)