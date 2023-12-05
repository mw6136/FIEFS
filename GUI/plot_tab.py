from tkinter import ttk

def create_plot_tab(notebook):
    frame = ttk.Frame(notebook, width=300, height=200)
    frame.grid(row=0, column=0, sticky="nsew")
    notebook.add(frame, text="Plot")

    # Add UI elements for the Plot tab
    # ...

    return frame
