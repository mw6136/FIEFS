import tkinter as tk
from tkinter import ttk

from GUI.GUI_tabs import (
    BoundaryConditionsTab,
    FlowParametersTab,
    GeometryTab,
    RunTab,
    TimeParametersTab,
)


class FlowSolverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flow Instability Eulerian Flow Solver (FIEFS)")
        self.geometry("800x600")
        self.notebook = ttk.Notebook(self)  # Make notebook an instance variable
        self.create_tabs()

    def create_tabs(self):
        # Create tabs using instances of classes
        geometry_tab = GeometryTab(self.notebook)
        flow_parameters_tab = FlowParametersTab(self.notebook)
        time_parameters_tab = TimeParametersTab(self.notebook)
        boundary_conditions_tab = BoundaryConditionsTab(self.notebook)
        run_tab = RunTab(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(geometry_tab, text="Geometry")
        self.notebook.add(flow_parameters_tab, text="Flow Parameters")
        self.notebook.add(time_parameters_tab, text="Time Parameters")
        self.notebook.add(boundary_conditions_tab, text="Boundary Conditions")
        self.notebook.add(run_tab, text="Run")

        # Bind the tab click event to the on_tab_click function
        self.notebook.bind("<ButtonRelease-1>", self.on_tab_click)

        # Pack the notebook into the main window
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights to make the frames expand with the window
        for _i in range(6):
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

    def on_tab_click(self, event):
        try:
            self.notebook.index("current")
        except tk.TclError:
            print("Error: Invalid tab")


if __name__ == "__main__":
    app = FlowSolverApp()
    app.mainloop()
