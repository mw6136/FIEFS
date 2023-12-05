from tkinter import ttk

def create_run_tab(notebook):
    frame = ttk.Frame(notebook, width=300, height=200)
    frame.grid(row=0, column=0, sticky="nsew")
    notebook.add(frame, text="Run")

    # Add UI elements for the Run tab
    # ...

    return frame
