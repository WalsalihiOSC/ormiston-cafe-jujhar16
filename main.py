import json
import tkinter as tk

from widgets import MenuWidget

MENU_COLUMN_COUNT = 5
# TODO: move to json file
DEFAULT_TAB = "Burgers"

class CafeInterface:
    def __init__(self, parent):
        root_frame = tk.Frame(parent)
        root_frame.grid(row=0, column=0, sticky='news')
        root_frame.grid_rowconfigure(0, weight=1)
        root_frame.grid_columnconfigure(0, weight=4)
        root_frame.grid_columnconfigure(1, weight=1, minsize=50)

        content_frame = tk.Frame(root_frame)
        content_frame.grid(row=0, column=0, sticky='news')
        content_frame.grid_rowconfigure(0, minsize=40)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        tab_frame = tk.Frame(content_frame, bg="blue")
        tab_frame.grid(row=0, column=0, sticky="news")

        menu = MenuWidget(content_frame, file_path="./menu.json", column_count=MENU_COLUMN_COUNT, selected_tab=DEFAULT_TAB)
        menu.grid(row=1, column=0, sticky="news")
        
        sidebar_frame = tk.Frame(root_frame, bg="gray")
        sidebar_frame.grid(row=0, column=1, sticky='news')

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('500x400')
    root.title("Cafe Interface")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    CafeInterface(root)
    root.mainloop()