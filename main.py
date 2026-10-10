import asyncio, logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)
from config import BOT_TOKEN
from database.mongo import init_indexes
from handlers.start import (start, addacc_start, addacc_name,
                            addacc_phone, cancel, ASK_NAME, ASK_PHONE, ASK_SESSION)
from handlers.accounts import (handle_session_input, my_accounts, remove_cmd)
from handlers.plans import my_plan
from handlers.owner import grant, broadcast

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def post_init(app):
    await init_indexes()

def main():
    app = (Application.builder()
           .token(BOT_TOKEN)
           .post_init(post_init)
           .build())

    # Add account conversation
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(addacc_start, pattern="^addacc$")],
        states={
            ASK_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, addacc_name)],
            ASK_PHONE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, addacc_phone)],
            ASK_SESSION: [MessageHandler(
                (filters.TEXT | filters.Document.ALL) & ~filters.COMMAND,
                handle_session_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )
    app.add_handler(conv)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remove", remove_cmd))
    app.add_handler(CommandHandler("grant", grant))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(my_accounts, pattern="^myacc$"))
    app.add_handler(CallbackQueryHandler(my_plan, pattern="^myplan$"))

    log.info("Bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
