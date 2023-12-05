from tkinter import ttk

def create_flow_parameters_tab(notebook):
    frame = ttk.Frame(notebook, width=300, height=200)
    frame.grid(row=0, column=0, sticky="nsew")
    notebook.add(frame, text="Flow Parameters")

    # Labels
    rho0_label = ttk.Label(frame, text="rho0:")
    rho0_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    rho1_label = ttk.Label(frame, text="rho1:")
    rho1_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    p0_label = ttk.Label(frame, text="p0:")
    p0_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    p1_label = ttk.Label(frame, text="p1:")
    p1_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    u0_label = ttk.Label(frame, text="u0:")
    u0_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    u1_label = ttk.Label(frame, text="u1:")
    u1_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

    # Entry widgets for user input
    rho0_entry = ttk.Entry(frame)
    rho0_entry.grid(row=0, column=1, padx=10, pady=10)

    rho1_entry = ttk.Entry(frame)
    rho1_entry.grid(row=1, column=1, padx=10, pady=10)

    p0_entry = ttk.Entry(frame)
    p0_entry.grid(row=2, column=1, padx=10, pady=10)

    p1_entry = ttk.Entry(frame)
    p1_entry.grid(row=3, column=1, padx=10, pady=10)

    u0_entry = ttk.Entry(frame)
    u0_entry.grid(row=4, column=1, padx=10, pady=10)

    u1_entry = ttk.Entry(frame)
    u1_entry.grid(row=5, column=1, padx=10, pady=10)


    return frame  # Don't forget to return the frame
