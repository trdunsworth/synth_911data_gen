import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import sys
import os

# Import the generator modules
# Ensure the current directory is in the path to import local modules
sys.path.append(os.getcwd())

try:
    import opt_synth911gen
    import synthvolgen
except ImportError as e:
    print(f"Error importing modules: {e}")
    # We will handle this gracefully in the UI if needed, or let it fail if critical

def run_script():
    selected_script = script_var.get()
    output_file = output_file_entry.get()
    
    # Disable run button while running
    run_button.config(state=tk.DISABLED)
    status_text.insert(tk.END, f"Starting {selected_script}...\n")
    status_text.see(tk.END)

    # Run in a separate thread to keep UI responsive
    thread = threading.Thread(target=execute_script, args=(selected_script, output_file))
    thread.start()

def execute_script(selected_script, output_file):
    try:
        if selected_script == "CAD Data Generation":
            # Retrieve parameters (add validation as needed)
            # For this demo, we'll use defaults or parse from entries if we added them
            # The original UI had placeholders param1/param2. 
            # We should map them to actual arguments if we want to use them.
            # For now, let's assume standard defaults or minimal args for safety.
            
            # Example: mapping param1 to num_records if it's a number
            try:
                num_records = int(param1_entry.get())
            except ValueError:
                num_records = 1000 # Default
            
            status_text.insert(tk.END, f"Generating {num_records} CAD records...\n")
            
            # Call the function directly
            df, _, _ = opt_synth911gen.generate_911_data(num_records=num_records)
            
            # Save to the specified output file
            if not output_file:
                output_file = "computer_aided_dispatch.csv"
            
            df.to_csv(output_file, index=False)
            status_text.insert(tk.END, f"Saved to {output_file}\n")

        elif selected_script == "Call Volume Generation":
             # Example: mapping param1 to num_rows
            try:
                num_rows = int(param1_entry.get())
            except ValueError:
                num_rows = 366 # Default
                
            status_text.insert(tk.END, f"Generating {num_rows} volume records...\n")
            
            # Call the function directly
            df = synthvolgen.generate_synthetic_data(num_rows=num_rows)
            
            if not output_file:
                output_file = "911_volume_data.csv"
                
            df.to_csv(output_file, index=False)
            status_text.insert(tk.END, f"Saved to {output_file}\n")
            
        root.after(0, lambda: status_text.insert(tk.END, "Execution complete.\n"))
        root.after(0, lambda: messagebox.showinfo("Success", "Data generation complete!"))

    except Exception as e:
        root.after(0, lambda: status_text.insert(tk.END, f"Error: {str(e)}\n"))
        root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
    finally:
        root.after(0, lambda: run_button.config(state=tk.NORMAL))

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

# Parameter input
# Renamed labels to be more descriptive based on usage
param1_label = tk.Label(root, text="Num Records/Rows:")
param1_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

param1_entry = tk.Entry(root, width=20)
param1_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
param1_entry.insert(0, "1000") # Default value

# Param 2 is currently unused in this simple implementation but kept for layout
param2_label = tk.Label(root, text="Parameter 2 (Unused):")
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

if __name__ == "__main__":
    root.mainloop()