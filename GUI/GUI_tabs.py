import tkinter as tk
from tkinter import ttk
import os

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

            entry.bind("<FocusOut>", lambda event, line=index[0], char=index[1], ent=entry, err_lbl=error_label: self.value_changed(event, line, char, ent, err_lbl))

    def value_changed(self, event, line_number, char_number, entry, error_label):
        new_value = entry.get()

        # Check if the entered value is a valid float

        
        if not self.check_type(new_value):
            error_label.config(text=f"\"{new_value}\" is not a valid float.", foreground="red", font=("Arial", 12))
            return
        
        error_label.config(text="✓", foreground="green", font=("Arial", 16))

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

    @staticmethod
    def check_type(value):
        value_type = float
        try:
            value_type(value)
            return True
        except ValueError:
            return False
        


class GeometryTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {"nx1": [3, 8], "nx2": [4, 8], "nvar": [5, 8], "ng": [6, 8],
                               "x1min": [8, 8], "x1max": [9, 8], "x2min": [10, 8], "x2max": [11, 8]}
        super().__init__(notebook, "Geometry", variables_and_lines)


class FlowParametersTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {"rho0": [14, 8], "rho1": [15, 8], "p0": [17, 8], "p1": [18, 8],
                               "u0": [20, 8], "u1": [21, 8], "pert_amp": [22, 8]}
        super().__init__(notebook, "Flow Parameters", variables_and_lines)


class TimeParametersTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {"CFL": [26, 8], "tmax": [27, 8], "gamma": [29, 8]}
        super().__init__(notebook, "Time Parameters", variables_and_lines)


class BoundaryConditionsTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {"Left BC": [32, 12], "Right BC": [33, 12], "Top BC": [34, 12], "Bottom BC": [35, 12]}
        super().__init__(notebook, "Boundary Conditions", variables_and_lines)

    def check_type(self, value):
        return isinstance(value, str)

'''
class OutputOptionsTab(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.width = 300
        self.height = 200
        self.variables_and_lines = {"Output Variables": [40, 19], "Output Frequency": [44, 19], "Data File Type": [46, 17]}
        self.create_widgets("Output Options")

        # Store the previous state of output variables
        self.prev_output_vars = [False, False, False, False]

        # Define error_label as an attribute
        self.error_label = None

    def create_widgets(self, tab_title):
        self.grid(row=0, column=0, sticky="nsew")
        label = ttk.Label(self, text=f"{tab_title}:")
        label.grid(row=0, column=0, columnspan=3, pady=10)

        options = ["x-velocity", "y-velocity", "density", "pressure"]

        for variable, index in self.variables_and_lines.items():
            label = ttk.Label(self, text=f"{variable}:")
            label.grid(row=index[0], column=0, padx=10, pady=10, sticky="w")

            # Check if the current variable is "Output Variables"
            if variable == "Output Variables":
                # Create a list of BooleanVar for each Checkbutton
                var_list = [tk.BooleanVar(value=False) for _ in range(4)]  # Assuming 4 options for output variables

                # Create Checkbuttons for multiple options
                checkboxes = []
                for i, option in enumerate(options):
                    checkbox = ttk.Checkbutton(self, text=option, variable=var_list[i], onvalue=True, offvalue=False, command=lambda i=i: self.on_output_var_change(i))
                    checkbox.grid(row=index[0] + i, column=1, padx=10, pady=5, sticky="w")
                    checkboxes.append(checkbox)

            elif variable == "Output Frequency":
                entry = ttk.Entry(self)
                entry.grid(row=index[0], column=1, padx=10, pady=10)
                entry.bind("<FocusOut>", lambda event: self.on_output_frequency_change(event, entry))  # Pass the entry widget

                # Define error_label as an attribute
                self.error_label = ttk.Label(self, text="", foreground="red")
                self.error_label.grid(row=index[0], column=2, padx=10, pady=10)

            elif variable == "Data File Type":
                # Create a StringVar to store the selected option
                data_file_type_var = tk.StringVar()

                # Create a Combobox for the dropdown menu
                file_type_combobox = ttk.Combobox(self, textvariable=data_file_type_var, values=["txt", "csv", "hdf5"])
                file_type_combobox.grid(row=index[0], column=1, padx=10, pady=10, sticky="w")
                file_type_combobox.set("txt")  # Set the default value
                file_type_combobox.bind("<<ComboboxSelected>>", lambda event: self.on_widget_change())

    def on_output_var_change(self, index):
        # Update the state of the clicked output variable
        self.prev_output_vars[index] = not self.prev_output_vars[index]

        # Get the currently checked variables
        checked_vars = [option for i, option in enumerate(["x-velocity", "y-velocity", "density", "pressure"]) if self.prev_output_vars[i]]

        print("Currently Checked Output Variables:", checked_vars)

    def on_output_frequency_change(self, event, entry):
        # Get the value of "Output Frequency" entry
        output_frequency_value = entry.get()

        # Check if the entered value is a valid float
        if not self.check_type(output_frequency_value):
            if self.error_label:
                self.error_label.config(text=f"\"{output_frequency_value}\" is not a valid float.", foreground="red", font=("Arial", 12))
            return

        # Check if self.error_label is not None before configuring it
        if self.error_label:
            self.error_label.config(text="ABC", foreground="red", font=("Arial", 12))

        print("Output Frequency Changed:", output_frequency_value)

    @staticmethod
    def check_type(value):
        value_type = float
        try:
            value_type(value)
            return True
        except ValueError:
            return False

                
class PlottingTab(BaseTab):
    def __init__(self, notebook):
        variables_and_lines = {"CFL": [40, 8], "tmax": [27, 8], "gamma": [29, 8]}
        super().__init__(notebook, "Time Parameters", variables_and_lines)
        '''





