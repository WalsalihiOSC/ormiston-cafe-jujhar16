import json
import subprocess
import time
import tkinter as tk
import tkinter.font
import PIL as pil

from widgets import MenuWidget

MENU_COLUMN_COUNT = 5
# TODO: move to json file
DEFAULT_TAB = "Burgers"

COLORS = [
    "#EBEAEA",
    "#FBFAFA",
]
# rainbow
# COLORS = [
#     "#e3e3ff",
#     "#dff2fd",
#     "#e2fce6",
#     "#fcfade",
#     "#ffeee2",
#     "#ffdbdb",
# ]


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

        # Create the menu widget before tabs in case the data fails to load
        menu = MenuWidget(content_frame, file_path="./menu.json",
                          column_count=MENU_COLUMN_COUNT, selected_tab=DEFAULT_TAB,
                          on_item_click=lambda name, info: self.add_to_order(name, info))
        menu.grid(row=1, column=0, sticky="news")
        if menu.data == None:
            root_frame.grid_columnconfigure(1, minsize=0)
            content_frame.grid_rowconfigure(0, minsize=0)
            return

        # TODO: move tabs to their own widget
        tab_frame = tk.Frame(
            content_frame, highlightbackground="black", highlightthickness=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)

        for index, category_name in enumerate(menu.data.keys()):
            tab_frame.grid_columnconfigure(index, uniform="tab")
            category_frame = tk.Frame(
                tab_frame, highlightbackground="black", highlightthickness=1)
            # rename variable
            category_frame.entered = False
            # Python doesnt close registers passed to closures :/
            # So to copy by value, we capture variables by passing them as default arguments

            def on_click(category_frame, category_name):
                # we don't want to call update if the tab is already selected,
                # as it flickers when updating
                if category_frame.entered and menu.selected_tab != category_name:
                    menu.selected_tab = category_name
                    menu.update()

            def on_enter(category_frame):
                category_frame.entered = True

            def on_leave(category_frame):
                category_frame.entered = False
            category_frame.bind(
                "<Enter>", lambda _, category_frame=category_frame: on_enter(category_frame))
            category_frame.bind(
                "<Leave>", lambda _, category_frame=category_frame: on_leave(category_frame))
            category_frame.bind_all('<Button-1>', lambda _, category_frame=category_frame,
                                    category_name=category_name: on_click(category_frame, category_name), add="+")
            category_frame.grid_rowconfigure(0, weight=1)
            category_frame.grid_columnconfigure(0, weight=1)
            category_frame.grid(row=0, column=index,
                                sticky="news", padx=(5, 0), pady=5)

            category_label = tk.Label(
                category_frame, text=category_name.title())
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
        tk.Label(sidebar_header_frame, text="ORDER", background="lightgray",
                 font=header_font).grid(row=0, column=0, padx=(10, 0), pady=5, sticky="nsw")

        clear_button_frame = tk.Frame(
            sidebar_header_frame, highlightbackground="black", highlightthickness=1)
        clear_button_frame.grid_rowconfigure(0, weight=1)
        clear_button_frame.grid_columnconfigure(0, weight=1)
        clear_button_frame.entered = False

        def clear_on_click():
            if clear_button_frame.entered:
                self.order_items.clear()
                for child in self.order_list_frame.winfo_children():
                    child.destroy()

        def clear_on_enter():
            clear_button_frame.entered = True

        def clear_on_leave():
            clear_button_frame.entered = False
        clear_button_frame.bind("<Enter>", lambda _: clear_on_enter())
        clear_button_frame.bind("<Leave>", lambda _: clear_on_leave())
        clear_button_frame.bind_all(
            '<Button-1>', lambda _: clear_on_click(), add="+")
        clear_button_frame.grid(
            row=0, column=1, sticky="news", padx=10, pady=10)
        tk.Label(clear_button_frame, text="CLEAR").grid(row=0, column=0)

        order_list_frame = tk.Frame(sidebar_frame, background="#FBFAFA")
        order_list_frame.grid_columnconfigure(0, weight=1)
        order_list_frame.grid_rowconfigure(0, weight=1)
        order_list_frame.grid(row=1, column=0, sticky="news", padx=10)

        canvas = tk.Canvas(
            order_list_frame, background="#FBFAFA", highlightthickness=0)
        # TODO: theme the scrollbar,
        # see: https://stackoverflow.com/questions/28375591/changing-the-appearance-of-a-scrollbar-in-tkinter-using-ttk-styles
        scrollbar = tk.Scrollbar(
            order_list_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="news")

        self.order_list_frame = tk.Frame(
            # sidebar_frame
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
                if (event.state & 0x1) != 0:
                    # TODO: test
                    canvas.xview_scroll(-event.delta, "units")
                else:
                    canvas.yview_scroll(-event.delta, "units")
        canvas.bind_all("<MouseWheel>", on_scroll)
        frame_id = canvas.create_window(
            (0, 0), window=self.order_list_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            frame_id, width=e.width))
        canvas["yscrollcommand"] = scrollbar.set
        canvas.grid(row=0, column=0, sticky="news")

        checkout_button_frame = tk.Frame(
            sidebar_frame, highlightbackground="black", highlightthickness=1)
        checkout_button_frame.grid_rowconfigure(0, weight=1)
        checkout_button_frame.grid_columnconfigure(0, weight=1)
        checkout_button_frame.entered = False

        def checkout_on_click():
            if checkout_button_frame.entered:
                checkout_popup = tk.Toplevel(root)
                x = root.winfo_x()
                y = root.winfo_y()
                rw = root.winfo_width()
                rh = root.winfo_height()
                w = 200
                h = 200
                checkout_popup.geometry(
                    "%dx%d+%d+%d" % (w, h, (x + rw/2) - (w/2), (y + rh/2) - (w/2)))
                checkout_popup.wait_visibility()
                checkout_popup.wm_attributes("-topmost", 1)
                button1_event = root.bind(
                    "<Button-1>", lambda _: "break", add="+")
                enter_event = root.bind("<Enter>", lambda _: "break", add="+")
                focusin_event = root.bind(
                    "<FocusIn>", lambda _: checkout_popup.focus_set(), add="+")

                def unbind_events(_):
                    root.unbind("<Button-1>", button1_event)
                    root.unbind("<Enter>", enter_event)
                    root.unbind("<FocusIn>", focusin_event)
                checkout_popup.bind('<Destroy>', unbind_events)

        def checkout_on_enter():
            checkout_button_frame.entered = True

        def checkout_on_leave():
            checkout_button_frame.entered = False
        checkout_button_frame.bind("<Enter>", lambda _: checkout_on_enter())
        checkout_button_frame.bind("<Leave>", lambda _: checkout_on_leave())
        checkout_button_frame.bind_all(
            '<Button-1>', lambda _: checkout_on_click(), add="+")
        checkout_button_frame.grid(
            row=3, column=0, sticky="news", padx=10, pady=10)
        tk.Label(checkout_button_frame, text="CHECKOUT",
                 font=header_font).grid(row=0, column=0)

    # TODO: sort order items alphabetically
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
            item_label.grid(row=0, column=0, sticky="w")
            tk.Label(item_frame, text=info["description"], background=color).grid(
                row=0, column=1, sticky="e")
            tk.Label(item_frame, text="${:,.2f}".format(
                info["price"]), background=color).grid(row=1, column=0, sticky="w")
            item_quantity_frame = tk.Frame(item_frame, background=color)
            item_quantity_frame.grid(row=1, column=1, sticky="e")

            # TODO: remove spacing above and below using canvas,
            # see: https://stackoverflow.com/questions/57481581/how-to-remove-vertical-padding-of-label-in-tkinter-completely
            # TODO: use SF Mono font and make label 3 chars wide minimum
            item_quantity_label = tk.Label(
                item_quantity_frame, text="1", background="lightgray")
            item_quantity_label.grid(row=0, column=1, sticky="e")
            self.order_items[name] = item_quantity_label

            # TODO: disable/gray-out `-` button when quantity == 0
            quantity_sub_button_frame = tk.Frame(
                item_quantity_frame, highlightbackground="black", highlightthickness=1)
            quantity_sub_button_frame.grid_rowconfigure(0, weight=1)
            quantity_sub_button_frame.grid_columnconfigure(0, weight=1)
            quantity_sub_button_frame.entered = False

            def sub_on_click(quantity_sub_button_frame, item_quantity_label, item_frame, name):
                if quantity_sub_button_frame.entered:
                    quantity = max(int(item_quantity_label["text"]) - 1, 0)
                    if quantity == 0:
                        # We use a global binding for clicking and the <Leave> event isnt called after this point,
                        # so we need to make sure `entered` is set to False
                        quantity_sub_button_frame.entered = False
                        self.order_items.pop(name)
                        item_frame.destroy()
                    else:
                        item_quantity_label["text"] = quantity

            def sub_on_enter(quantity_sub_button_frame):
                quantity_sub_button_frame.entered = True

            def sub_on_leave(quantity_sub_button_frame):
                quantity_sub_button_frame.entered = False
            quantity_sub_button_frame.bind(
                "<Enter>", lambda _, quantity_sub_button_frame=quantity_sub_button_frame: sub_on_enter(quantity_sub_button_frame))
            quantity_sub_button_frame.bind(
                "<Leave>", lambda _, quantity_sub_button_frame=quantity_sub_button_frame: sub_on_leave(quantity_sub_button_frame))
            quantity_sub_button_frame.bind_all('<Button-1>',
                                               lambda _,
                                               quantity_sub_button_frame=quantity_sub_button_frame,
                                               item_quantity_label=item_quantity_label,
                                               item_frame=item_frame,
                                               name=name:
                                               sub_on_click(
                                                   quantity_sub_button_frame, item_quantity_label, item_frame, name),
                                               add="+")
            quantity_sub_button_frame.grid(row=0, column=0)
            tk.Label(quantity_sub_button_frame, text="-").grid(row=0, column=0)

            quantity_add_button_frame = tk.Frame(
                item_quantity_frame, highlightbackground="black", highlightthickness=1)
            quantity_add_button_frame.grid_rowconfigure(0, weight=1)
            quantity_add_button_frame.grid_columnconfigure(0, weight=1)
            quantity_add_button_frame.entered = False

            def add_on_click(quantity_add_button_frame, item_quantity_label):
                if quantity_add_button_frame.entered:
                    item_quantity_label["text"] = int(
                        item_quantity_label["text"]) + 1

            def add_on_enter(quantity_add_button_frame):
                quantity_add_button_frame.entered = True

            def add_on_leave(quantity_add_button_frame):
                quantity_add_button_frame.entered = False
            quantity_add_button_frame.bind(
                "<Enter>", lambda _, quantity_add_button_frame=quantity_add_button_frame: add_on_enter(quantity_add_button_frame))
            quantity_add_button_frame.bind(
                "<Leave>", lambda _, quantity_add_button_frame=quantity_add_button_frame: add_on_leave(quantity_add_button_frame))
            quantity_add_button_frame.bind_all('<Button-1>', lambda _, quantity_add_button_frame=quantity_add_button_frame,
                                               item_quantity_label=item_quantity_label: add_on_click(quantity_add_button_frame, item_quantity_label), add="+")
            quantity_add_button_frame.grid(row=0, column=2)
            tk.Label(quantity_add_button_frame, text="+").grid(row=0, column=0)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x500')
    root.title("Cafe Interface")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    CafeInterface(root)
    root.mainloop()
