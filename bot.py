# rev 26 date: 1404-06-17 Time 06:15pm
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import tenders
import about_us
import contact_us
import projects
import admin
import utils
import config
import news
import faq
import registration
import threading
import notifications

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    print(f"Starting for user {user_id}, type: {type(update.message)}, {type(update.callback_query)}")  # ?????
    config = utils.load_config()
    if config["update_mode"] and user_id not in utils.load_admins():
        if update.message:
            update.message.reply_text("???? ?? ??? ??-\\???????? ???? ????? ????? ?????? ????\\.", parse_mode='MarkdownV2')
        elif update.callback_query:
            update.callback_query.message.reply_text("???? ?? ??? ??-\\???????? ???? ????? ????? ?????? ????\\.", parse_mode='MarkdownV2')
        return

    welcome_message = "?? <b>??? ????? ?? ???? ???? ???? ????? ?????? ?????</b> ??\n???? ??????? ?????? ??? ???????? ???? ????:"
    keyboard = [
        [InlineKeyboardButton("?? ?????????", callback_data='tenders_page_0')],
        [InlineKeyboardButton("?? ???? ????????", callback_data='projects_page_0')],
        [InlineKeyboardButton("?? ?????", callback_data='news')],
        [InlineKeyboardButton("? FAQ", callback_data='faq')],
        [InlineKeyboardButton("?? ???????", callback_data='registration')],
        [InlineKeyboardButton("?? ???? ?? ??", callback_data='contact_us'), InlineKeyboardButton("?? ?????? ??", callback_data='about_us')]
    ]
    if user_id in utils.load_admins():
        keyboard.append([InlineKeyboardButton("?? ???????", callback_data='admin_dashboard')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        if update.message:
            message = update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='HTML')
        elif update.callback_query and update.callback_query.message:
            try:
                message = update.callback_query.message.edit_text(welcome_message, reply_markup=reply_markup, parse_mode='HTML')
            except Exception as e:
                print(f"Error editing message: {e}")
                message = update.callback_query.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='HTML')
        else:
            message = context.bot.send_message(chat_id=user_id, text=welcome_message, reply_markup=reply_markup, parse_mode='HTML')
        context.user_data['last_message_id'] = message.message_id
    except Exception as e:
        print(f"Error sending message: {e}")

    stats = utils.load_stats()
    stats["users"].add(user_id)
    utils.save_stats(stats)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    config = utils.load_config()
    if config["update_mode"] and user_id not in utils.load_admins():
        query.message.reply_text("???? ?? ??? ??-\\???????? ???? ????? ????? ?????? ????\\.", parse_mode='MarkdownV2')
        return

    # ??? ???? ???? ??? ??? ?? ??? ?? show_internal_numbers ????
    if query.data != 'show_internal_numbers':
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        except Exception as e:
            print(f"Error deleting message: {e}")

    if query.data.startswith('tenders_page_'):
        page = int(query.data.replace('tenders_page_', ''))
        tenders.show_tenders(update, context, page)
    elif query.data.startswith('projects_page_'):
        page = int(query.data.replace('projects_page_', ''))
        projects.handle_projects(update, context, page)
    elif query.data.startswith('download_'):
        tender_id = query.data.replace('download_', '')
        tenders.send_document(update, context, tender_id)
    elif query.data.startswith('more_details_'):
        tender_id = query.data.replace('more_details_', '')
        tenders.show_more_details(update, context, tender_id)
    elif query.data == 'about_us':
        about_us.show_about_us(update, context)
    elif query.data == 'board_members':
        about_us.show_board_members(update, context)
    elif query.data == 'org_chart':
        about_us.show_org_chart(update, context)
    elif query.data == 'contact_us':
        contact_us.show_contact_us(update, context)
    elif query.data == 'show_internal_numbers':
        contact_us.handle_callback(update, context)
    elif query.data == 'news':
        news.show_news(update, context)
    elif query.data in ['news_page_prev', 'news_page_next'] or query.data.startswith('full_news_'):
        news.button_handler(update, context)
    elif query.data == 'faq':
        faq.show_faq(update, context)
    elif query.data in ['faq_page_prev', 'faq_page_next'] or query.data.startswith('faq_answer_'):
        faq.button_handler(update, context)
    elif query.data == 'registration':
        registration.registration_menu(update, context)
    elif query.data == 'admin_dashboard':
        if user_id in utils.load_admins():
            admin.show_admin_dashboard(update, context)
    elif query.data == 'manage_tenders':
        if user_id in utils.load_admins():
            admin.manage_tenders(update, context)
    elif query.data == 'add_tender':
        if user_id in utils.load_admins():
            admin.add_tender(update, context)
    elif query.data.startswith('renew_tender_'):
        if user_id in utils.load_admins():
            tender_id = query.data.replace('renew_tender_', '')
            tenders.renew_tender(update, context, tender_id)
    elif query.data == 'main_menu' or query.data == 'back':
        start(update, context)

    query.answer()

def main() -> None:
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(registration.conv_handler)  # ????? ???? ConversationHandler
    dp.add_handler(CallbackQueryHandler(button))

    import threading
    scheduler_thread = threading.Thread(target=admin.run_scheduler, args=(updater,), daemon=True)
    scheduler_thread.start()
    notification_thread = threading.Thread(target=notifications.run_notifications, args=(updater,), daemon=True)
    notification_thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()