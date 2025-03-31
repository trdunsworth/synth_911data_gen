import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # For combobox (dropdown)

def run_script():
    selected_script = script_var.get()
    output_file = output_file_entry.get()
    
    # Placeholder for parameter retrieval
    param1 = param1_entry.get()
    param2 = param2_entry.get()

    status_text.insert(tk.END, f"Running {selected_script}...\n")
    status_text.insert(tk.END, f"Output file: {output_file}\n")
    status_text.insert(tk.END, f"Parameter 1: {param1}, Parameter 2: {param2}\n")

    # Placeholder for actual script execution logic
    # Replace with your script logic, passing parameters
    # Example:
    # if selected_script == "CAD Data Generation":
    #     generate_cad_data(output_file, param1, param2)
    # elif selected_script == "Call Volume Generation":
    #     generate_call_volume(output_file, param1, param2)

    status_text.insert(tk.END, "Script execution complete.\n")

def select_output_file():
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if filename:
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, filename)

# Main window
root = tk.Tk()
root.title("911 Data Generator")

# Script selection
script_label = tk.Label(root, text="Select Script:")
script_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

scripts = ["CAD Data Generation", "Call Volume Generation"]
script_var = tk.StringVar(root)
script_dropdown = ttk.Combobox(root, textvariable=script_var, values=scripts)
script_dropdown.grid(row=0, column=1, sticky="we", padx=5, pady=5)
script_dropdown.current(0)  # Set default selection

# Output file selection
output_label = tk.Label(root, text="Output File:")
output_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

output_file_entry = tk.Entry(root, width=50)
output_file_entry.grid(row=1, column=1, sticky="we", padx=5, pady=5)

output_button = tk.Button(root, text="Browse", command=select_output_file)
output_button.grid(row=1, column=2, padx=5, pady=5)

# Parameter input (placeholder)
param1_label = tk.Label(root, text="Parameter 1:")
param1_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

param1_entry = tk.Entry(root, width=20)
param1_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

param2_label = tk.Label(root, text="Parameter 2:")
param2_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

param2_entry = tk.Entry(root, width=20)
param2_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

# Run button
run_button = tk.Button(root, text="Run", command=run_script)
run_button.grid(row=4, column=1, pady=10)

# Status display
status_label = tk.Label(root, text="Status:")
status_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)

status_text = tk.Text(root, height=10, width=60)
status_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()