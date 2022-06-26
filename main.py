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
            on_item_click=lambda name, info: self.add_to_order(name, info))
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
            category_frame.bind_all('<Button-1>', lambda _, category_frame=category_frame,
                category_name=category_name: on_click(category_frame, category_name), add="+")
            category_frame.grid_rowconfigure(0, weight=1)
            category_frame.grid_columnconfigure(0, weight=1)
            category_frame.grid(row=0, column=index, sticky="news", padx=(5, 0), pady=5)

            category_label = tk.Label(category_frame, text=category_name)
            category_label.grid(row=0, column=0, sticky="news")
        
        sidebar_frame = tk.Frame(root_frame, background="lightgray")
        sidebar_frame.grid_columnconfigure(0, weight=1)
        sidebar_frame.grid_rowconfigure(1, weight=1)
        sidebar_frame.grid(row=0, column=1, sticky='news')

        sidebar_header_frame = tk.Frame(sidebar_frame, background="lightgray")
        sidebar_header_frame.grid_columnconfigure(0, weight=1)
        sidebar_header_frame.grid(row=0, column=0, sticky="news")

        header_font = tk.font.nametofont("TkDefaultFont").copy()
        header_font["size"] = 20
        tk.Label(sidebar_header_frame, text="Order:", background="lightgray",
            font=header_font).grid(row=0, column=0, padx=5, pady=5, sticky="nsw")

        clear_button_frame = tk.Frame(sidebar_header_frame, highlightbackground="black", highlightthickness=1)
        clear_button_frame.grid_rowconfigure(0, weight=1)
        clear_button_frame.grid_columnconfigure(0, weight=1)
        clear_button_frame.grid(row=0, column=1, sticky="news", padx=10, pady=10)
        tk.Label(clear_button_frame, text="CLEAR").grid(row=0, column=0)

        order_list_frame = tk.Frame(sidebar_frame, background="#FBFAFA")
        order_list_frame.grid_columnconfigure(0, weight=1)
        order_list_frame.grid_rowconfigure(0, weight=1)
        order_list_frame.grid(row=1, column=0, sticky="news", padx=10)

        canvas = tk.Canvas(order_list_frame, background="#FBFAFA", highlightthickness=0)
        # TODO: theme the scrollbar,
        # see: https://stackoverflow.com/questions/28375591/changing-the-appearance-of-a-scrollbar-in-tkinter-using-ttk-styles
        scrollbar = tk.Scrollbar(order_list_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="news")

        self.order_list_frame = tk.Frame(
            #sidebar_frame
            canvas, background="#FBFAFA")
        self.order_list_frame.grid_columnconfigure(0, weight=1)
        # self.order_list_frame.grid(row=1, column=0, sticky='news')
        self.order_list_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.entered = False
        # these functions cant be named "on_enter", etc. because that will result in them
        # overriding the previous definition for categories :(
        def c_on_enter(_):
            canvas.entered = True
        def c_on_leave(_):
            canvas.entered = False
        canvas.bind("<Enter>", c_on_enter)
        canvas.bind("<Leave>", c_on_leave)
        # TODO: this only works on macos, for windows & linux support,
        # see: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        def on_scroll(event):
            if canvas.entered:
                canvas.yview_scroll(-event.delta, "units")
        canvas.bind_all("<MouseWheel>", on_scroll)
        frame_id = canvas.create_window((0, 0), window=self.order_list_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
        canvas["yscrollcommand"] = scrollbar.set
        canvas.grid(row=0, column=0, sticky="news")

        checkout_button_frame = tk.Frame(sidebar_frame, highlightbackground="black", highlightthickness=1)
        checkout_button_frame.grid_rowconfigure(0, weight=1)
        checkout_button_frame.grid_columnconfigure(0, weight=1)
        checkout_button_frame.grid(row=3, column=0, sticky="news", padx=10, pady=10)
        tk.Label(checkout_button_frame, text="CHECKOUT", font=header_font).grid(row=0, column=0)

    def add_to_order(self, name, info):
        item_quantity_label = self.order_items.get(name)
        if item_quantity_label != None:
            item_quantity_label["text"] = int(item_quantity_label["text"]) + 1
        else:
            color = COLORS[self.color_counter]
            item_frame = tk.Frame(self.order_list_frame, background=color)
            self.color_counter += 1
            if self.color_counter == len(COLORS):
                self.color_counter = 0
            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid(sticky="news")
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