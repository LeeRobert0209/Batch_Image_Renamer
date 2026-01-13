
import tkinter as tk
from tkinterdnd2 import TkinterDnD
from src.gui.app import MainApp

def main():
    # 检测是否支持拖拽库
    try:
        root = TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
    
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
