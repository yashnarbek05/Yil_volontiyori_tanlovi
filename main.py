from telegram import Update
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ApplicationBuilder

from bot.service import IS_SUB, start, catch_subscribed, LANGUAGE, language, cancel, send_messagee, error_handler, CONTACT \
    , receive_number, FULLNAME_VOLONTIYOR, fullname_volontiyor, eng_yaxshi_volontiyorlar, eng_yaxshi_tashabbuskorlar, comment_volontiyor, \
    COMMENT_VOLONTIYOR, COMMENT_TASHABBUSKOR, FULLNAME_TASHABBUSKOR, comment_tashabbuskor, fullname_tashabbuskor, TAVSIYA, \
    GURUH, guruh, tavsiya

from config import BOT_TOKEN

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).read_timeout(300).write_timeout(300).build()


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            IS_SUB: [
                CallbackQueryHandler(catch_subscribed, pattern="^sub$")
            ],
            LANGUAGE: [CommandHandler('cancel', cancel),CallbackQueryHandler(language)],
            CONTACT: [CommandHandler('cancel', cancel),MessageHandler(filters.CONTACT, receive_number)],
            FULLNAME_VOLONTIYOR: [CommandHandler('cancel', cancel),MessageHandler(filters.TEXT, fullname_volontiyor)],
            COMMENT_VOLONTIYOR: [CommandHandler('cancel', cancel),MessageHandler(filters.TEXT, comment_volontiyor)],
            FULLNAME_TASHABBUSKOR: [CommandHandler('cancel', cancel),MessageHandler(filters.TEXT, fullname_tashabbuskor)],
            COMMENT_TASHABBUSKOR: [CommandHandler('cancel', cancel),MessageHandler(filters.TEXT, comment_tashabbuskor)],
            GURUH: [CommandHandler('cancel', cancel),MessageHandler(filters.TEXT, guruh)],
            TAVSIYA: [CommandHandler('cancel', cancel),MessageHandler(filters.TEXT, tavsiya)],
            
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    )   

    application.add_handler(CommandHandler("eng_yaxshi_volontiyorlar", eng_yaxshi_volontiyorlar))
    application.add_handler(CommandHandler("eng_yaxshi_tashabbuskorlar", eng_yaxshi_tashabbuskorlar))
    application.add_handler(CommandHandler("sm", send_messagee))

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()
