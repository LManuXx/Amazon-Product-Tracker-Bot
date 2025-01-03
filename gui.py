# gui.py

import sys
import os
import asyncio
import threading
import itertools
import time
import subprocess

import tkinter as tk
from tkinter import messagebox, scrolledtext

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import InvalidToken

from bot import run_bot 

class PriceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Price Tracker Bot")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # ---- VARIABLES DE INSTANCIA ----
        self.bot_process = None
        self.running = False

        # ---- COLORES PARA LOS TEMAS ----
        self.themes = {
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

        # Variable para el tema actual
        self.current_theme = "Oscuro"

        # ---- CREACIÓN DE WIDGETS ----
        self.create_widgets()

        # ---- CARGAR TOKEN EXISTENTE ----
        self.load_existing_token()

        # ---- APLICAR TEMA INICIAL ----
        self.apply_theme(self.current_theme)

        # ---- MANEJO DEL CIERRE DE LA VENTANA ----
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Etiqueta y Entry para el token
        self.token_label = tk.Label(self.root, text="Ingresa el Token del Bot de Telegram:", font=("Segoe UI", 14))
        self.token_label.pack(pady=10)

        self.token_entry = tk.Entry(self.root, width=50, font=("Segoe UI", 14))
        self.token_entry.pack(pady=5)

        # Botones Iniciar y Detener
        self.start_button = tk.Button(
            self.root, 
            text="Iniciar Bot", 
            command=self.save_token_and_run_bot,
            font=("Segoe UI", 12), 
            padx=10, 
            pady=5
        )
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(
            self.root, 
            text="Detener Bot", 
            command=self.stop_bot,
            font=("Segoe UI", 12), 
            padx=10, 
            pady=5
        )
        self.stop_button.pack(pady=10)

        # Tema y Estado
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.status_label = tk.Label(self.root, text="Estado: Inactivo", font=("Segoe UI", 12))
        self.status_label.pack(pady=20)

        # Área de log
        self.log_text = scrolledtext.ScrolledText(
            self.root, 
            height=15, 
            font=("Segoe UI", 10), 
            state=tk.DISABLED
        )
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

        # Botón para cambiar tema
        self.theme_toggle_button = tk.Button(
            self.root, 
            text="\u2600", 
            command=self.toggle_theme, 
            font=("Segoe UI", 12), 
            width=4
        )
        self.theme_toggle_button.place(relx=0.95, rely=0.02, anchor="ne")

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    async def validate_token(self, token):
        """
        Verifica si el token ingresado es válido haciendo una petición
        asíncrona a la API de Telegram.
        """
        try:
            bot = Bot(token=token)
            await bot.get_me()
            return True
        except InvalidToken:
            self.log_message("Error: Token inválido ingresado.")
            return False
        except Exception as e:
            self.log_message(f"Error al validar el token: {e}")
            return False

    def load_existing_token(self):
        load_dotenv()
        existing_token = os.getenv("TOKEN")
        if existing_token:
            self.token_entry.insert(0, existing_token)

    def animate_status(self):
        for frame in itertools.cycle([".", "..", "..."]):
            if not self.running:
                self.status_label.config(text="Estado: Inactivo")
                break
            self.status_label.config(text=f"Estado: Ejecutando el bot{frame}")
            time.sleep(0.5)

    def start_animation(self):
        threading.Thread(target=self.animate_status, daemon=True).start()

    def stop_animation(self):
        self.status_label.config(text="Estado: Inactivo")

    def save_token_and_run_bot(self):
        token = self.token_entry.get()
        if not token:
            messagebox.showerror("Error", "El token no puede estar vacío.")
            self.log_message("Error: El token no puede estar vacío.")
            return

        # Iniciar la validación en un hilo separado para no bloquear la GUI
        threading.Thread(target=self.validate_and_run_bot, args=(token,), daemon=True).start()

    def validate_and_run_bot(self, token):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        token_valid = loop.run_until_complete(self.validate_token(token))
        if not token_valid:
            self.log_message("Error: El token ingresado no es válido.")
            messagebox.showerror("Error", "El token ingresado no es válido.")
            return

        try:
            with open(".env", "w") as env_file:
                env_file.write(f"TOKEN={token}\n")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el token: {e}")
            self.log_message(f"Error: No se pudo guardar el token: {e}")
            return

        self.log_message("Token guardado correctamente.")

        # Verificar si el bot ya se está ejecutando
        if self.bot_process and self.bot_process.poll() is None:
            messagebox.showinfo("Información", "El bot ya está en ejecución.")
            self.log_message("Información: El bot ya está en ejecución.")
            return

        # Inicia un nuevo proceso en modo BOT
        try:
            self.bot_process = subprocess.Popen(
                [sys.executable, "main.py", "--run-bot"],
                close_fds=True
            )
            self.running = True
            self.start_animation()
            self.log_message("Bot iniciado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el bot: {e}")
            self.log_message(f"Error al iniciar el bot: {e}")

    def stop_bot(self):
        if self.bot_process and self.bot_process.poll() is None:
            self.bot_process.terminate()
            self.bot_process = None
            self.running = False
            self.stop_animation()
            messagebox.showinfo("Éxito", "El bot se detuvo correctamente.")
            self.log_message("Bot detenido correctamente.")
        else:
            messagebox.showinfo("Información", "El bot no está en ejecución.")
            self.log_message("Intento de detener el bot cuando no está en ejecución.")

    def apply_theme(self, theme):
        colors = self.themes[theme]
        self.root.configure(bg=colors["bg"])
        self.token_label.config(bg=colors["bg"], fg=colors["fg"])
        self.token_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"])
        self.start_button.config(
            bg=colors["button_bg"], 
            fg=colors["button_fg"], 
            relief="flat", 
            highlightthickness=0, 
            borderwidth=5
        )
        self.stop_button.config(
            bg=colors["button_stop_bg"], 
            fg=colors["button_stop_fg"], 
            relief="flat", 
            highlightthickness=0, 
            borderwidth=5
        )
        self.log_text.config(bg=colors["log_bg"], fg=colors["log_fg"])
        self.status_label.config(bg=colors["bg"], fg=colors["status_fg"])
        self.theme_toggle_button.config(
            bg=colors["button_bg"], 
            fg=colors["button_fg"], 
            relief="flat", 
            highlightthickness=0
        )

    def toggle_theme(self):
        new_theme = "Claro" if self.current_theme == "Oscuro" else "Oscuro"
        self.current_theme = new_theme
        self.apply_theme(new_theme)

    def on_closing(self):
        if self.bot_process and self.bot_process.poll() is None:
            if messagebox.askokcancel("Salir", "El bot está en ejecución. ¿Deseas detener el bot y salir?"):
                self.stop_bot()
                self.root.destroy()
        else:
            self.root.destroy()
