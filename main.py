import asyncio, logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)
from config import BOT_TOKEN
from database.mongo import init_indexes
from handlers.start import (
    start, addacc_start, addacc_name, addacc_phone, cancel,
    ASK_NAME, ASK_PHONE, ASK_SESSION
)
from handlers.accounts import (
    handle_session_input, my_accounts, remove_cmd,
    react_menu, views_menu, joinevc_menu, rand_menu
)
from handlers.plans import my_plan
from handlers.owner import grant, broadcast
from handlers.features import (
    react_cmd, views_cmd, joinvc_cmd, randomize_cmd
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger(__name__)

async def post_init(app: Application):
    await init_indexes()
    log.info("✅ Mongo indexes ready")

def main():
    app = (Application.builder()
           .token(BOT_TOKEN)
           .post_init(post_init)
           .build())

    # ---------- Add-account conversation ----------
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
        allow_reentry=True,
        per_message=False,
    )
    app.add_handler(conv)

    # ---------- Commands ----------
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remove", remove_cmd))
    app.add_handler(CommandHandler("grant", grant))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("react", react_cmd))
    app.add_handler(CommandHandler("views", views_cmd))
    app.add_handler(CommandHandler("joinvc", joinvc_cmd))
    app.add_handler(CommandHandler("randomize", randomize_cmd))

    # ---------- Callback buttons ----------
    app.add_handler(CallbackQueryHandler(my_accounts, pattern="^myacc$"))
    app.add_handler(CallbackQueryHandler(my_plan, pattern="^myplan$"))
    app.add_handler(CallbackQueryHandler(react_menu, pattern="^react$"))
    app.add_handler(CallbackQueryHandler(views_menu, pattern="^views$"))
    app.add_handler(CallbackQueryHandler(joinevc_menu, pattern="^joinevc$"))
    app.add_handler(CallbackQueryHandler(rand_menu, pattern="^rand$"))

    log.info("🚀 Bot started. Send /start to begin.")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
