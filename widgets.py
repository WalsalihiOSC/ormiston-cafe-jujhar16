import json
from tkinter import Frame, Label

class MenuWidget(Frame):
    # TODO: should this take a json object, file object or string instead?
    def __init__(self, parent, file_path, column_count, selected_tab):
        Frame.__init__(self, parent)
        self.selected_tab = selected_tab
        self.column_count = column_count

        try:
            with open(file_path) as file:
                self.data = json.load(file)
        except EnvironmentError:
            self.data = None

        # the frame is populated outside the try/except so only errors relating to io and json parsing
        # are handled
        if self.data == None:
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
            Label(self, text="failed to load menu").grid(sticky="news")
            return
        
        # make menu items auto-size and uniform in width
        for column in range(self.column_count):
            # TODO: also make rows uniform="item"?
            self.grid_columnconfigure(column, weight=1, uniform="item")
        self.update()
    def update(self):
        # TODO: save scroll state and reuse menu item widgets,
        # grid_remove or grid_forget instead of destroy
        for child in self.winfo_children():
            child.destroy()
        for index, (item_name, item_info) in enumerate(self.data[self.selected_tab].items()):
            item_frame = Frame(self, highlightbackground="gray", highlightthickness=2)
            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_rowconfigure(0, weight=0)
            item_frame.grid_rowconfigure(1, weight=0)
            item_frame.grid(row=int(index/self.column_count), column=int(index%self.column_count),
                sticky="news", padx=5, pady=5)

            placeholder_frame = Frame(item_frame, background="gray", height=60)
            placeholder_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)

            name_label = WrappingLabel(item_frame, text=item_name)
            name_label.grid(row=1, column=0, sticky="news")

# https://stackoverflow.com/questions/62485520/how-to-wrap-the-text-in-a-tkinter-label-dynamically
class WrappingLabel(Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
