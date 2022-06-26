import json
import tkinter as tk
import tkinter.font

from widgets import MenuWidget

MENU_COLUMN_COUNT = 5
# TODO: move to json file
DEFAULT_TAB = "Burgers"

COLORS = [
    "#e3e3ff",
    "#dff2fd",
    "#e2fce6",
    "#fcfade",
    "#ffeee2",
    "#ffdbdb",
]

class CafeInterface:
    def __init__(self, root):
        self.order_items = {}
        self.color_counter = 0

        root_frame = tk.Frame(root)
        root_frame.grid_rowconfigure(0, weight=1)
        root_frame.grid_columnconfigure(0, weight=2)
        root_frame.grid_columnconfigure(1, minsize=300)
        root_frame.grid(row=0, column=0, sticky='news')

        content_frame = tk.Frame(root_frame)
        content_frame.grid_rowconfigure(0, minsize=45)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid(row=0, column=0, sticky='news')

        # TODO: move tabs to their own widget
        tab_frame = tk.Frame(content_frame, highlightbackground="black", highlightthickness=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)

        menu = MenuWidget(content_frame, file_path="./menu.json",
            column_count=MENU_COLUMN_COUNT, selected_tab=DEFAULT_TAB,
            on_item_click=lambda name, info: self.add_to_order(name, info), root=root)
        menu.grid(row=1, column=0, sticky="news")

        for index, category_name in enumerate(menu.data.keys()):
            tab_frame.grid_columnconfigure(index, uniform="tab")
            category_frame = tk.Frame(tab_frame, highlightbackground="black", highlightthickness=1)
            # rename variable
            category_frame.entered = False
            # Python doesnt close registers passed to closures :/
            # So to copy by value, we capture variables by passing them as default arguments
            def on_click(category_frame, category_name):
                if category_frame.entered:
                    menu.selected_tab = category_name
                    menu.update()
            def on_enter(category_frame):
                category_frame.entered = True
            def on_leave(category_frame):
                category_frame.entered = False
            category_frame.bind("<Enter>", lambda _, category_frame=category_frame: on_enter(category_frame))
            category_frame.bind("<Leave>", lambda _, category_frame=category_frame: on_leave(category_frame))
            root.bind('<Button-1>', lambda _, category_frame=category_frame,
                category_name=category_name: on_click(category_frame, category_name), add="+")
            category_frame.grid_rowconfigure(0, weight=1)
            category_frame.grid_columnconfigure(0, weight=1)
            category_frame.grid(row=0, column=index, sticky="news", padx=(5, 0), pady=5)

            category_label = tk.Label(category_frame, text=category_name)
            category_label.grid(row=0, column=0, sticky="news")
        
        self.sidebar_frame = tk.Frame(root_frame, background="lightgray")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid(row=0, column=1, sticky='news')
        font = tk.font.nametofont("TkDefaultFont").copy()
        font["size"] = 20
        tk.Label(self.sidebar_frame, text="Order:", background="lightgray",
            font=font).grid(padx=5, pady=5, sticky="nsw")

    def add_to_order(self, name, info):
        item_quantity_label = self.order_items.get(name)
        if item_quantity_label != None:
            item_quantity_label["text"] = int(item_quantity_label["text"]) + 1
        else:
            color = COLORS[self.color_counter]
            item_frame = tk.Frame(self.sidebar_frame, background=color)
            self.color_counter += 1
            if self.color_counter == len(COLORS):
                self.color_counter = 0
            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid(sticky="news", pady=(0, 5))
            item_label = tk.Label(item_frame, text=name, background=color)
            item_label.grid(row=0, column=0, sticky="nws")
            item_quantity_label = tk.Label(item_frame, text="1", background=color)
            item_quantity_label.grid(row=0, column=1, sticky="nws")
            self.order_items[name] = item_quantity_label
        

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x500')
    root.title("Cafe Interface")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    CafeInterface(root)
    root.mainloop()