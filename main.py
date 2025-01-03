import sys
import os
import asyncio
import threading
import itertools
import time
import subprocess
import multiprocessing

import tkinter as tk
from tkinter import messagebox, scrolledtext

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import InvalidToken
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters
)

# Importa tus módulos locales (asegúrate de que estén en la misma carpeta):
from commands import (
    start, add_url, list_urls, check_price, remove_url, 
    show_history, help_command, menu_handler, handle_user_input
)
from database import init_db
from price_checker import check_prices

# ---- VARIABLES GLOBALES PARA LA GUI ----
bot_process = None
running = False

# ---- COLORES PARA LOS TEMAS ----
themes = {
    "Oscuro": {
        "bg": "#282a36",
        "fg": "#f8f8f2",
        "entry_bg": "#44475a",
        "entry_fg": "#f8f8f2",
        "button_bg": "#6272a4",
        "button_fg": "#f8f8f2",
        "button_stop_bg": "#ff5555",
        "button_stop_fg": "#f8f8f2",
        "log_bg": "#44475a",
        "log_fg": "#f8f8f2",
        "status_fg": "#f8f8f2"
    },
    "Claro": {
        "bg": "#f8f8f2",
        "fg": "#282a36",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "button_bg": "#50fa7b",
        "button_fg": "#282a36",
        "button_stop_bg": "#ff5555",
        "button_stop_fg": "#f8f8f2",
        "log_bg": "#ffffff",
        "log_fg": "#000000",
        "status_fg": "#282a36"
    }
}

# --------------------------------------------------------------------
#                           MODO BOT
# --------------------------------------------------------------------
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

# --------------------------------------------------------------------
#                           MODO GUI
# --------------------------------------------------------------------
def run_gui():
    """
    Lógica para ejecutar la GUI (adaptado de gui_launcher.py).
    """
    global bot_process, running

    def log_message(message):
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, f"{message}\n")
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)

    async def validate_token(token):
        """
        Verifica si el token ingresado es válido haciendo una petición
        asíncrona a la API de Telegram.
        """
        try:
            bot = Bot(token=token)
            await bot.get_me()
            return True
        except InvalidToken:
            log_message("Error: Token inválido ingresado.")
            return False
        except Exception as e:
            log_message(f"Error al validar el token: {e}")
            return False

    def load_existing_token():
        load_dotenv()
        return os.getenv("TOKEN")

    def animate_status():
        for frame in itertools.cycle([".", "..", "..."]):
            if not running:
                status_label.config(text="Estado: Inactivo")
                break
            status_label.config(text=f"Estado: Ejecutando el bot{frame}")
            time.sleep(0.5)

    def start_animation():
        threading.Thread(target=animate_status, daemon=True).start()

    def stop_animation():
        status_label.config(text="Estado: Inactivo")

    def save_token_and_run_bot():
        global bot_process, running

        token = token_entry.get()
        if not token:
            messagebox.showerror("Error", "El token no puede estar vacío.")
            log_message("Error: El token no puede estar vacío.")
            return

        loop = asyncio.get_event_loop()
        token_valid = loop.run_until_complete(validate_token(token))
        if not token_valid:
            log_message("Error: El token ingresado no es válido.")
            messagebox.showerror("Error", "El token ingresado no es válido.")
            return

        try:
            with open(".env", "w") as env_file:
                env_file.write(f"TOKEN={token}\n")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el token: {e}")
            log_message(f"Error: No se pudo guardar el token: {e}")
            return

        log_message("Token guardado correctamente.")

        # Verificar si el bot ya se está ejecutando
        if bot_process and bot_process.poll() is None:
            messagebox.showinfo("Información", "El bot ya está en ejecución.")
            log_message("Información: El bot ya está en ejecución.")
            return

        # Inicia un nuevo proceso en modo BOT
        try:
            bot_process = subprocess.Popen(
                [sys.executable, sys.argv[0], "--run-bot"],
                close_fds=True
            )
            running = True
            start_animation()
            log_message("Bot iniciado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el bot: {e}")
            log_message(f"Error al iniciar el bot: {e}")

    def stop_bot():
        global bot_process, running
        if bot_process and bot_process.poll() is None:
            bot_process.terminate()
            bot_process = None
            running = False
            stop_animation()
            messagebox.showinfo("Éxito", "El bot se detuvo correctamente.")
            log_message("Bot detenido correctamente.")
        else:
            messagebox.showinfo("Información", "El bot no está en ejecución.")
            log_message("Intento de detener el bot cuando no está en ejecución.")

    def apply_theme(theme):
        colors = themes[theme]
        root.configure(bg=colors["bg"])
        token_label.config(bg=colors["bg"], fg=colors["fg"])
        token_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"])
        start_button.config(bg=colors["button_bg"], fg=colors["button_fg"], 
                            relief="flat", highlightthickness=0, borderwidth=5)
        stop_button.config(bg=colors["button_stop_bg"], fg=colors["button_stop_fg"], 
                           relief="flat", highlightthickness=0, borderwidth=5)
        log_text.config(bg=colors["log_bg"], fg=colors["log_fg"])
        status_label.config(bg=colors["bg"], fg=colors["status_fg"])
        theme_toggle_button.config(bg=colors["button_bg"], fg=colors["button_fg"], 
                                   relief="flat", highlightthickness=0)

    def toggle_theme():
        current_theme = theme_var.get()
        new_theme = "Claro" if current_theme == "Oscuro" else "Oscuro"
        theme_var.set(new_theme)
        apply_theme(new_theme)

    # --------------- CREACIÓN DE LA VENTANA ---------------
    root = tk.Tk()
    root.title("Price Tracker Bot")
    root.geometry("800x600")
    root.minsize(800, 600)

    # Etiqueta y Entry para el token
    token_label = tk.Label(root, text="Ingresa el Token del Bot de Telegram:", font=("Segoe UI", 14))
    token_label.pack(pady=10)

    token_entry = tk.Entry(root, width=50, font=("Segoe UI", 14))
    token_entry.pack(pady=5)

    existing_token = load_existing_token()
    if existing_token:
        token_entry.insert(0, existing_token)

    # Botones Iniciar y Detener
    start_button = tk.Button(root, text="Iniciar Bot", command=save_token_and_run_bot,
                             font=("Segoe UI", 12), padx=10, pady=5)
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Detener Bot", command=stop_bot,
                            font=("Segoe UI", 12), padx=10, pady=5)
    stop_button.pack(pady=10)

    # Tema y Estado
    theme_var = tk.StringVar(value="Oscuro")
    status_label = tk.Label(root, text="Estado: Inactivo", font=("Segoe UI", 12))
    status_label.pack(pady=20)

    # Área de log
    log_text = tk.Text(root, height=15, font=("Segoe UI", 10), state=tk.DISABLED)
    log_text.pack(pady=10, fill=tk.BOTH, expand=True)

    # Botón para cambiar tema
    theme_toggle_button = tk.Button(root, text="\u2600", command=toggle_theme, 
                                    font=("Segoe UI", 12), width=4)
    theme_toggle_button.place(relx=0.95, rely=0.02, anchor="ne")

    # Aplicar tema inicial
    apply_theme("Oscuro")

    # Iniciar bucle de la GUI
    root.mainloop()

# --------------------------------------------------------------------
#                    PUNTO DE ENTRADA ÚNICO
# --------------------------------------------------------------------
if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        multiprocessing.freeze_support()

    # Si se pasó --run-bot, ejecutamos el bot
    if "--run-bot" in sys.argv:
        run_bot()
    else:
        # De lo contrario, lanzamos la GUI
        run_gui()
