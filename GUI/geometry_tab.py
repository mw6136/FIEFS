from tkinter import ttk

def create_geometry_tab(notebook):
    frame = ttk.Frame(notebook, width=300, height=200)
    frame.grid(row=0, column=0, sticky="nsew")
    notebook.add(frame, text="Geometry & Grid")
    return frame
