# main.py

import sys
import multiprocessing

from gui import PriceTrackerGUI  
from bot import run_bot

import tkinter as tk

def run_gui():
    root = tk.Tk()
    app = PriceTrackerGUI(root)
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
