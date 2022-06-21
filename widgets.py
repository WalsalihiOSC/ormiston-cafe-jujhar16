import tkinter as tk
class MenuWidget(tk.Frame):
    def __init__(self, parent, file):
        with open("menu.json") as file:
            json.load(file)