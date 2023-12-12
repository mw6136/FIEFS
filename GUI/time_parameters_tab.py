from tkinter import ttk
import os

def is_valid_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def value_changed(event, line_number, char_number, entry, error_label):
    new_value = entry.get()

    # Check if the entered value is a valid float
    if not is_valid_float(new_value):
        error_label.config(text=f"\"{new_value}\" is not a valid float.", foreground="red", font=("Arial",12))
        return
    

    error_label.config(text="✓",foreground="green", font=("Arial", 16))

    file_path = os.path.abspath(os.path.join("inputs", "GUI_input_file.txt"))
    
    # Read existing lines from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Update the substring starting from the specified index in each line
    if line_number < len(lines):
        line = lines[line_number]
        if char_number < len(line):
            # Delete everything after the specified character index
            lines[line_number] = line[:char_number] + new_value + '\n'

            # Write the modified lines back to the file
            with open(file_path, 'w') as file:
                file.writelines(lines)


def create_time_parameters_tab(notebook):
    frame = ttk.Frame(notebook, width=300, height=200)
    frame.grid(row=0, column=0, sticky="nsew")
    notebook.add(frame, text="Time Parameters")

    # Variables and line numbers in the file
    variables_and_lines = {"CFL": [26, 8], "tmax": [27, 8], "gamma": [29, 8]}

    # Labels, Entry widgets, and Error labels
    for variable, index in variables_and_lines.items():
        label = ttk.Label(frame, text=f"{variable}:")
        label.grid(row=index[0], column=0, padx=10, pady=10, sticky="w")

        entry = ttk.Entry(frame)
        entry.grid(row=index[0], column=1, padx=10, pady=10)

        error_label = ttk.Label(frame, text="", foreground="red")
        error_label.grid(row=index[0], column=2, padx=10, pady=10)

        entry.bind("<FocusOut>", lambda event, line=index[0], char=index[1], ent=entry, err_lbl=error_label: value_changed(event, line, char, ent, err_lbl))

    return frame
