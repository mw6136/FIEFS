

#GUI capabilities:
'''
  Grid Information:
  - 

  Flow Parameters:
  - rho1
  - rho2
  - p0
  - p1
  - u0
  - u1
  - per_am

  Time info:
  - CFL
  - tmax
  - gamma

  Boundary Conditions:
  - left_bc
  - right_bc
  - top_bc
  - bottom_bc

  Output Options:
  - Output Variables: x-velocity, y-velocity, density, pressure
  - Output Frequency: 
  - Data File Type: txt, csv, hdf5

  Plotting:
  - variables to plot: rho, u, v, et
  - labels: rhow, u, v, e_t
  - color maps: jet, ocean, ocean, hot
  - stability name: Kelvin-Helmholtz Instability
  - style mode: True/False
'''
import tkinter as tk
from tkinter import ttk
from GUI.geometry_tab import create_geometry_tab
from GUI.flow_parameters_tab import create_flow_parameters_tab
from GUI.bcs_tab import create_bcs_tab
from GUI.time_parameters_tab import create_time_parameters_tab
from GUI.outputs_tab import create_outputs_tab
from GUI.run_tab import create_run_tab
from GUI.plot_tab import create_plot_tab


def on_tab_click(event):
    selected_tab = notebook.index(notebook.select())
    print(f"Tab {selected_tab + 1} clicked!")

# Create the main window
root = tk.Tk()
root.title("Flow Instability Eulerian Flow Solver (FIEFS)")

# Set the initial size of the window (width x height)
root.geometry("800x600")

# Create a notebook (tabbed container)
notebook = ttk.Notebook(root)

# Create tabs using functions from other files
geometry_tab = create_geometry_tab(notebook)
flow_parameters_tab = create_flow_parameters_tab(notebook)
bcs_tab = create_bcs_tab(notebook)
time_parameters_tab = create_time_parameters_tab(notebook)
outputs_tab = create_outputs_tab(notebook)
run_tab = create_run_tab(notebook)
plot_tab = create_plot_tab(notebook)

# Bind the tab click event to the on_tab_click function
notebook.bind("<ButtonRelease-1>", on_tab_click)

# Pack the notebook into the main window
notebook.grid(row=0, column=0, sticky="nsew")

# Configure grid weights to make the frames expand with the window
for i in range(6):
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

# Start the main event loop
root.mainloop()
