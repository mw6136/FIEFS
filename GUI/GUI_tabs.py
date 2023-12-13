import os
import tkinter as tk
from tkinter import ttk


class BaseTab(ttk.Frame):
    def __init__(self, notebook, tab_title, variables_and_lines):
        super().__init__(notebook)
        self.width = 300
        self.height = 200
        self.variables_and_lines = variables_and_lines
        self.create_widgets(tab_title)

    def create_widgets(self, tab_title):
        self.grid(row=0, column=0, sticky="nsew")
        label = ttk.Label(self, text=f"{tab_title}:")
        label.grid(row=0, column=0, columnspan=3, pady=10)

        for variable, index in self.variables_and_lines.items():
            label = ttk.Label(self, text=f"{variable}:")
            label.grid(row=index[0], column=0, padx=10, pady=10, sticky="w")

            entry = ttk.Entry(self)
            entry.grid(row=index[0], column=1, padx=10, pady=10)

            error_label = ttk.Label(self, text="", foreground="red")
            error_label.grid(row=index[0], column=2, padx=10, pady=10)

            entry.bind(
                "<FocusOut>",
                lambda event, line=index[0], char=index[
                    1
                ], ent=entry, err_lbl=error_label: self.value_changed(
                    event, line, char, ent, err_lbl
                ),
            )

    def value_changed(self, event, line_number, char_number, entry, error_label):
        new_value = entry.get()

        if not self.check_type(new_value, error_label):
            return
        self.write_to_file(event, line_number, char_number, new_value, error_label)

    def write_to_file(self, event, line_number, char_number, new_value, error_label):
        file_path = os.path.abspath(os.path.join("inputs", "inputs.IN"))

        # Read existing lines from the file
        with open(file_path) as file:
            lines = file.readlines()

        # Update the substring starting from the specified index in each line
        if line_number < len(lines):
            line = lines[line_number]
            if char_number < len(line):
                # Delete everything after the specified character index
                lines[line_number] = line[:char_number] + new_value + "\n"

                # Write the modified lines back to the file
                with open(file_path, "w") as file:
                    file.writelines(lines)

    @staticmethod
    def check_type(value, error_label):
        value_type = float
        try:
            value_type(value)
            error_label.config(text="✓", foreground="green", font=("Arial", 16))
            return True
        except ValueError:
            error_label.config(
                text=f'"{value}" is not a valid float.',
                foreground="red",
                font=("Arial", 12),
            )
            return False


class GeometryTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {
            "nx1": [3, 8],
            "nx2": [4, 8],
            "nvar": [5, 8],
            "ng": [6, 8],
            "x1min": [8, 8],
            "x1max": [9, 8],
            "x2min": [10, 8],
            "x2max": [11, 8],
        }
        super().__init__(notebook, "Geometry", variables_and_lines)


class FlowParametersTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {
            "rho0": [14, 8],
            "rho1": [15, 8],
            "p0": [17, 8],
            "p1": [18, 8],
            "u0": [20, 8],
            "u1": [21, 8],
            "pert_amp": [22, 8],
        }
        super().__init__(notebook, "Flow Parameters", variables_and_lines)


class TimeParametersTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {"CFL": [26, 8], "tmax": [27, 8], "gamma": [29, 8]}
        super().__init__(notebook, "Time Parameters", variables_and_lines)


class BoundaryConditionsTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {
            "Left BC": [32, 12],
            "Right BC": [33, 12],
            "Top BC": [34, 12],
            "Bottom BC": [35, 12],
        }
        super().__init__(notebook, "Boundary Conditions", variables_and_lines)

    def check_type(self, value, error_label):
        valid_values = {"transmissive", "periodic", "wall"}
        if value.lower() in valid_values:
            error_label.config(text="✓", foreground="green", font=("Arial", 16))
            return True
        else:
            error_label.config(
                text="Entry must be 'transmissive', 'periodic', or 'wall'",
                foreground="red",
                font=("Arial", 12),
            )
            return False


class RunTab(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.create_widgets()

    def create_widgets(self):
        self.output_text = tk.Text(self, height=10, width=80, wrap=tk.WORD)
        self.output_text.pack(pady=10)

        run_button = ttk.Button(self, text="RUN", command=self.run_command)
        run_button.pack(pady=10)

    def run_command(self):
        header = "Copy the following lines of code into any Linux command prompt:\n"
        command1 = "conda create -n environment python=3.9 anaconda"
        command2 = "python FIEFS.py -p inputs"

        # Clear previous content
        self.output_text.delete("1.0", tk.END)

        # Insert the header and indented commands into the Text widget
        self.output_text.insert(tk.END, header)
        self.output_text.insert(tk.END, f"    {command1}\n")
        self.output_text.insert(tk.END, f"    {command2}\n")

        # Enable the Text widget for copying
        self.output_text.config(state=tk.NORMAL)
