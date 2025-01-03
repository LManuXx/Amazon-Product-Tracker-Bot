# bot.py

import os
import asyncio
import threading

from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters
)


from commands import (
    start, add_url, list_urls, check_price, remove_url, 
    show_history, help_command, menu_handler, handle_user_input
)
from database import init_db
from price_checker import check_prices

def run_bot():
    """
    Lógica para ejecutar el BOT (adaptado de tracker.py).
    """

    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        raise ValueError("El token no está configurado en el archivo .env")

    # Deshabilitar webhook antes de usar polling
    try:
        bot = Bot(token=TOKEN)
        bot.delete_webhook(drop_pending_updates=True)
        print("Webhook eliminado correctamente.")
    except Exception as e:
        print(f"Advertencia: No se pudo eliminar el webhook: {e}")

    # ----------------- SCHEDULER / VERIFICACIÓN PERIÓDICA -----------------
    async def periodic_check(interval):
        await check_prices()  # Primera verificación
        while True:
            await asyncio.create_task(check_prices()) 
            await asyncio.sleep(interval)

    def run_scheduler():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(periodic_check(3600))  # Cada 1 hora

    def start_scheduler():
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()

    # ----------------- BOT MAIN -----------------
    def bot_main():
        init_db()

        application = Application.builder().token(TOKEN).build()

        # Registrar comandos
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("add", add_url))
        application.add_handler(CommandHandler("list", list_urls))
        application.add_handler(CommandHandler("checkprice", check_price))
        application.add_handler(CommandHandler("remove", remove_url))
        application.add_handler(CommandHandler("history", show_history))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(menu_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))

        start_scheduler()

        # Iniciar el bot
        application.run_polling(drop_pending_updates=True)

    bot_main()
