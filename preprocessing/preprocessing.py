"""
Fichier principal de preprocessing
By Titouan Verdier
"""
import tkinter as tk
from tkinter import ttk
import pandas as pd
import json as j
import os

# Get the script directory for relative file paths
script_dir = os.path.dirname(os.path.abspath(__file__))

verbose = False
def toggle_verbose():
    global verbose
    verbose = not verbose
    verbose_button.config(bg="green" if verbose else "lightgrey")
    verbose_window.insert(tk.END, f"Verbose mode: {'ON' if verbose else 'OFF'}\n")
    verbose_window.see(tk.END)

def check_file_presence():
    if os.path.exists(os.path.join(script_dir, "custom_dataset.json")):
        processed_button.config(state=tk.NORMAL); del_button.config(state=tk.NORMAL)
        processed_button.config(bg="orange"); del_button.config(bg="red")
        root.after(20, check_file_presence)
    else:
        processed_button.config(state=tk.DISABLED); del_button.config(state=tk.DISABLED)
        processed_button.config(bg="lightgrey"); del_button.config(bg="lightgrey")
        root.after(20, check_file_presence)

def check_undefined_status():
    if undefined_toggle.get():
        outlier_button.config(state=tk.NORMAL)
        if outlier_toggle.get():
            outlier_button.config(bg="green")
        elif not outlier_toggle.get():
            outlier_button.config(bg="red")
        outlier_description2.place_forget()
        root.after(20, check_undefined_status)
    else:
        outlier_button.config(state=tk.DISABLED)
        outlier_button.config(bg="lightgrey")
        outlier_description2.place(x=480, y=285)
        root.after(20, check_undefined_status)

# Paramètres d'affichage
window = [1200, 700] # Taille de la fenêtre principale et dataframe

# Convertir le json en DataFrame pandas
datas = os.path.join(script_dir, "flattened_datas.json")
df = pd.read_json(datas)

def produce_dataset_TKinter():
    global df
    if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, "Producing custom dataset\n") # VERBOSE début !

    selected_attrs = [attr for attr, var in state_vars.items() if var.get()]
    if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Selected attributes: {selected_attrs}\n") # VERBOSE affichage des attributs sélectionnés

    custom_df = df[selected_attrs].copy()

    if undefined_toggle.get():
        initial_count = len(custom_df)
        custom_df.dropna(inplace=True)
        if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Removed {initial_count - len(custom_df)} packets with undefined values.\n") # VERBOSE affichage du nombre de paquets supprimés car attribut non défini

    if outlier_toggle.get():
        for attr in selected_attrs:
            if pd.api.types.is_numeric_dtype(custom_df[attr]):
                mean = custom_df[attr].mean()
                std_dev = custom_df[attr].std()
                initial_count = len(custom_df)
                custom_df = custom_df[(custom_df[attr] >= mean - outlier_threshold.get() * std_dev) & (custom_df[attr] <= mean + outlier_threshold.get() * std_dev)]
                if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Removed {initial_count - len(custom_df)} packets outside {outlier_threshold.get()} standard deviations for attribute '{attr}'.\n") # VERBOSE affichage du nombre de paquets supprimés pour chaque attribut

    if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Remaining packets after processing: {len(custom_df)}\n") # VERBOSE sauvegarde du dataset
    custom_df.to_json(os.path.join(script_dir, "custom_dataset.json"), orient="records", indent=2)
    verbose_window.see(tk.END); verbose_window.insert(tk.END, "custom_dataset.json generated successfully.\n") # VERBOSE terminé !

###############################
#                             #
#           FILTRES           #
#                             #
###############################

current_filters = {}
saved_filter_values = {}

def open_filter_window(df):
    global current_filters, saved_filter_values
    win = tk.Toplevel(root)
    win.title("Filtrage des données")
    win.geometry("1200x650")
    
    current_filters = {}
    
    canvas = tk.Canvas(win)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    row, col = 0, 0
    max_rows = 10
    col_width = 280
    
    for colname in df.columns:
        dtype = df[colname].dtype
        
        # Frame pour chaque filtre
        filter_frame = tk.Frame(scrollable_frame, bd=1, relief="groove", padx=5, pady=3)
        filter_frame.place(x=10 + (col * col_width), y=10 + (row * 55), width=col_width - 20, height=50)
        
        tk.Label(filter_frame, text=colname, font=("Helvetica", 9, "bold")).pack(anchor="w")
        
        if pd.api.types.is_numeric_dtype(dtype):
            saved = saved_filter_values.get(colname, {})
            min_var = tk.StringVar(value=saved.get("min", ""))
            max_var = tk.StringVar(value=saved.get("max", ""))
            
            entry_frame = tk.Frame(filter_frame)
            entry_frame.pack(anchor="w")
            tk.Label(entry_frame, text="Min:", font=("Helvetica", 8)).pack(side="left")
            tk.Entry(entry_frame, textvariable=min_var, width=8).pack(side="left", padx=2)
            tk.Label(entry_frame, text="Max:", font=("Helvetica", 8)).pack(side="left")
            tk.Entry(entry_frame, textvariable=max_var, width=8).pack(side="left", padx=2)
            current_filters[colname] = ("numeric", min_var, max_var)
            
        elif pd.api.types.is_string_dtype(dtype):
            saved = saved_filter_values.get(colname, {})
            str_var = tk.StringVar(value=saved.get("value", ""))
            tk.Entry(filter_frame, textvariable=str_var, width=30).pack(anchor="w")
            current_filters[colname] = str_var
            
        elif pd.api.types.is_bool_dtype(dtype):
            saved = saved_filter_values.get(colname, {})
            filter_enabled = tk.BooleanVar(value=saved.get("enabled", False))
            bool_var = tk.BooleanVar(value=saved.get("value", True))
            
            check_frame = tk.Frame(filter_frame)
            check_frame.pack(anchor="w")
            tk.Checkbutton(check_frame, variable=filter_enabled, text="Actif", font=("Helvetica", 8)).pack(side="left")
            tk.Checkbutton(check_frame, variable=bool_var, text="=True", font=("Helvetica", 8)).pack(side="left")
            current_filters[colname] = (filter_enabled, bool_var)
        
        row += 1
        if row >= max_rows:
            row = 0
            col += 1
    
    # Calculer la taille du scrollable_frame
    total_cols = col + 1 if row > 0 else col
    scrollable_frame.config(width=total_cols * col_width, height=max_rows * 55 + 20)
    
    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")
    
    def save_current_filters():
        global saved_filter_values
        saved_filter_values = {}
        for colname, val in current_filters.items():
            if isinstance(val, tuple) and len(val) == 3 and val[0] == "numeric":
                saved_filter_values[colname] = {"type": "numeric", "min": val[1].get(), "max": val[2].get()}
            elif isinstance(val, tuple) and len(val) == 2 and isinstance(val[0], tk.BooleanVar):
                saved_filter_values[colname] = {"type": "bool", "enabled": val[0].get(), "value": val[1].get()}
            elif isinstance(val, tk.StringVar):
                saved_filter_values[colname] = {"type": "string", "value": val.get()}
        if verbose:
            verbose_window.insert(tk.END, "Filters saved in memory.\n")
            verbose_window.see(tk.END)

    # Bouton sauvegarder en bas de la fenêtre
    save_button = tk.Button(win, text="SAVE FILTERS CONFIGURATION", bg="green", fg="white", font=("Helvetica", 12, "bold"), command=save_current_filters)
    save_button.place(x=10, y=610)

def apply_filters():
    global current_filters
    if not current_filters:
        if verbose:
            verbose_window.insert(tk.END, "Please configure filters first.\n")
            verbose_window.see(tk.END)
        return
    filtered_df = df.copy()
    for col, val in current_filters.items():
        if isinstance(val, tuple) and len(val) == 3 and val[0] == "numeric":
            min_str = val[1].get().strip()
            max_str = val[2].get().strip()
            if min_str != "":
                try:
                    min_val = float(min_str)
                    filtered_df = filtered_df[filtered_df[col] >= min_val]
                except ValueError:
                    pass
            if max_str != "":
                try:
                    max_val = float(max_str)
                    filtered_df = filtered_df[filtered_df[col] <= max_val]
                except ValueError:
                    pass
        elif isinstance(val, tuple) and len(val) == 2 and isinstance(val[0], tk.BooleanVar) and isinstance(val[1], tk.BooleanVar):
            filter_enabled, bool_val = val
            if filter_enabled.get():
                filtered_df = filtered_df[filtered_df[col] == bool_val.get()]
        elif isinstance(val, tk.StringVar):
            if val.get() != "":
                filtered_df = filtered_df[filtered_df[col].str.contains(val.get(), case=False, na=False)]
    
    if verbose: 
        verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Filtered DataFrame: {len(filtered_df)} rows remaining.\n")
    
    show_filtered_result(filtered_df)

def show_filtered_result(filtered_df):
    win = tk.Toplevel(root)
    win.title("Filtering results")
    win.geometry(f"{window[0]}x{window[1]}")

    frame = tk.Frame(win)
    frame.pack(expand=True, fill='both')

    tree = ttk.Treeview(frame, columns=list(filtered_df.columns), show="headings")
    
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    for col in filtered_df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    for _, row in filtered_df.iterrows():
        tree.insert("", "end", values=list(row))

# def export_filtered_dataframe(): 
# à implémenter plus tard

###############################
#                             #
#      FENÊTRE DATAFRAME      #
#                             #
###############################

# DATAFRAME COMPLET

def open_dataframe_window():
    win = tk.Toplevel(root)
    win.title("Visualisation du DataFrame complet")
    win.geometry(f"{window[0]}x{window[1]}")

    # Frame principale pour contenir le Treeview
    frame = tk.Frame(win)
    frame.pack(expand=True, fill='both')

    tree = ttk.Treeview(frame, columns=list(df.columns), show="headings")
    
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')

    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky='nsew')

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

# DATAFRAME RAFFINÉ

def open_processed_dataframe_window():
    processed_datas = os.path.join(script_dir, "custom_dataset.json")
    processed_df = pd.read_json(processed_datas)

    win = tk.Toplevel(root)
    win.title("Visualisation du DataFrame raffiné")
    win.geometry(f"{window[0]}x{window[1]}")

    # Frame principale pour contenir le Treeview
    frame = tk.Frame(win)
    frame.pack(expand=True, fill='both')

    tree = ttk.Treeview(frame, columns=list(processed_df.columns), show="headings")
    
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')

    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky='nsew')

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    for col in processed_df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    for _, row in processed_df.iterrows():
        tree.insert("", "end", values=list(row))

################################
#                              #
#      FENÊTRE PRINCIPALE      #
#                              #
################################

root = tk.Tk()
root.title("DATAS PRE-PROCESSING TOOL")
root.geometry(f"{window[0]}x{window[1]}")

# Verbose mode
verbose_button = tk.Button(root, text="TOGGLE VERBOSE MODE", width=30, bg="lightgrey", font=("Helvetica", 10, "bold"), command=lambda: toggle_verbose())
verbose_button.place(x=window[0]//2, y=530, anchor=tk.CENTER)

verbose_window = tk.Text(root, height=5, width=130, font=("Helvetica", 10))
verbose_window.place(x=window[0]//2, y=600, anchor=tk.CENTER)

# Titre
title = tk.Label(root, text="DATAS PRE-PROCESSING TOOL", font=("Helvetica", 18, "bold"))
title.place(x=window[0]//2, y=20, anchor=tk.CENTER)

# Récupérer les attributs du json
with open(os.path.join(script_dir, 'flattened_datas.json'), 'r') as f:
    data = j.load(f)
    attributes = list(data[0].keys())
    if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Attributes available in the JSON: {attributes}\n") # VERBOSE affichage des caractéristiques des paquets

# Créer les variables d'état pour les boutons
state_vars = {}
for attr in attributes:
    state_vars[attr] = tk.BooleanVar(value=False)
if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"State variables created for attributes: {list(state_vars.keys())}\n") # VERBOSE affichage des variables d'état des boutons

# Créer les boutons
buttons = {}
attr_buttons_label = tk.Label(root, text="Available attributes for the dataset", font=("Helvetica", 12, "bold"))
attr_buttons_label.place(x=10, y=50)
i, j = 0, 0

all_on_button = tk.Button(root, text="ENABLE ALL", font=("Helvetica", 10, "bold"), width=20, bg="blue", fg="white", command=lambda: [state_vars[attr].set(True) or buttons[f"btn_{attr}"].config(bg="green") for attr in attributes])
all_on_button.place(x=10, y=80)

all_off_button = tk.Button(root, text="DISABLE ALL", font=("Helvetica", 10, "bold"), width=20, bg="blue", fg="white", command=lambda: [state_vars[attr].set(False) or buttons[f"btn_{attr}"].config(bg="red") for attr in attributes])
all_off_button.place(x=190, y=80)

for attr in attributes:
    def button_cmd(a=attr):
        def toggle():
            if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Button for attribute '{a}' clicked. New state : {not state_vars[a].get()}\n") # VERBOSE affichage de l'état après le clic
            state_vars[a].set(not state_vars[a].get())
            buttons[f"btn_{a}"].config(bg="green" if state_vars[a].get() else "red")
        return toggle
    buttons[f"btn_{attr}"] = tk.Button(root, text=attr, width=10, fg="white", bg="green" if state_vars[attr].get() else "red", command=button_cmd())
    buttons[f"btn_{attr}"].place(x=10 + (j * 100), y=120 + i*30)
    i = (i + 1) % 7; j += (i == 0)

# Boutons valeurs non définies
undefined_label = tk.Label(root, text="Handle undefined attributes", font=("Helvetica", 12, "bold"))
undefined_label.place(x=500, y=50)
undefined_description = tk.Label(root, text="Remove packets with at least one undefined value", font=("Helvetica", 8))
undefined_description.place(x=500, y=75)

undefined_button = tk.Button(root, text="UNDEFINED ATTRIBUTES HANDLING", width=30, bg="red", fg="white", font=("Helvetica", 10, "bold"), command=lambda: toggle_undefined())
undefined_button.place(x=500, y=100)

# Bouton valeurs abberrantes
outlier_label = tk.Label(root, text="Handle outlier values", font=("Helvetica", 12, "bold"))
outlier_label.place(x=500, y=150)
outlier_description = tk.Label(root, text="Remove packets with a distance from the mean", font=("Helvetica", 8))
outlier_description.place(x=500, y=175)
outlier_description = tk.Label(root, text="greater than n standard deviations", font=("Helvetica", 8))
outlier_description.place(x=500, y=190)
outlier_button = tk.Button(root, text="OUTLIER VALUES HANDLING", width=30, bg="red", fg="white", font=("Helvetica", 10, "bold"), command=lambda: toggle_outliers())
outlier_button.place(x=500, y=215)

outlier_description2 = tk.Label(root, text="Needs undefined attributes handling enabled", font=("Helvetica", 10 , "bold"), fg="red")
outlier_description2.place(x=480, y=285)

outlier_unit_label = tk.Label(root, text="n", font=("Helvetica", 10, "bold"))
outlier_unit_label.place(x=500, y=263)
outlier_threshold = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, length=230)
outlier_threshold.place(x=520, y=245)

outlier_toggle = tk.BooleanVar(value=False)
def toggle_outliers():
    if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Outlier values handling toggled to: {not outlier_toggle.get()}\n") # VERBOSE affichage de l'état après le clic
    outlier_toggle.set(not outlier_toggle.get())
    outlier_button.config(bg="green" if outlier_toggle.get() else "red")

undefined_toggle = tk.BooleanVar(value=False)
def toggle_undefined():
    if verbose: verbose_window.see(tk.END); verbose_window.insert(tk.END, f"Undefined attribute handling toggled to: {not undefined_toggle.get()}\n") # VERBOSE affichage de l'état après le clic
    undefined_toggle.set(not undefined_toggle.get())
    undefined_button.config(bg="green" if undefined_toggle.get() else "red")

check_undefined_status()

# Boutons supplémentaires
filter_label = tk.Label(root, text="Open filtering window", font=("Helvetica", 12, "bold"))
filter_label.place(x=850, y=50)

filter_button = tk.Button(root, text="OPEN FILTERS CONFIGURATION", fg="white", width=30, bg="blue", font=("Helvetica", 10, "bold"), command=lambda: open_filter_window(df))
filter_button.place(x=850, y=80)

filter_apply_button = tk.Button(root, text="APPLY FILTERS", width=30, bg="orange", font=("Helvetica", 10, "bold"), command=apply_filters)
filter_apply_button.place(x=850, y=120)

# filter_export_button = tk.Button(root, text="EXPORT FILTERED DATA", width=30, bg="purple", fg="white", font=("Helvetica", 10, "bold"), command=export_filtered_dataframe)
# filter_export_button.place(x=850, y=160)
# """ BOUTON NON FONCTIONNEL POUR L'INSTANT """
# filter_export_button.config(state=tk.DISABLED); filter_export_button.config(bg="lightgrey")

# Bouton pour produire le dataset JSON
execute_label = tk.Label(root, text="Generate custom dataset with selected attributes", font=("Helvetica", 12, "bold"))
execute_label.place(x=window[0]//2-400, y=400, anchor=tk.CENTER)

execute_button = tk.Button(root, text="GENERATE DATASET", width=30, bg="orange", font=("Helvetica", 12, "bold"), command=produce_dataset_TKinter)
execute_button.place(x=window[0]//2-400, y=430, anchor=tk.CENTER)

del_button = tk.Button(root, text="DELETE CUSTOM DATASET", width=25, bg="red", fg="white", font=("Helvetica", 8, "bold"), command=lambda: [os.remove(os.path.join(script_dir, "custom_dataset.json")), check_file_presence()] if os.path.exists(os.path.join(script_dir, "custom_dataset.json")) else None)
del_button.place(x=window[0]//2-400, y=470, anchor=tk.CENTER)

# Bouton pour afficher le DataFrame dans une nouvelle fenêtre
dataframe_label = tk.Label(root, text="View the complete DataFrame", font=("Helvetica", 12, "bold"))
dataframe_label.place(x=window[0]//2, y=400, anchor=tk.CENTER)

dataframe_button = tk.Button(root, text="SHOW COMPLETE DATAFRAME", width=30, bg="orange", font=("Helvetica", 12, "bold"), command=open_dataframe_window)
dataframe_button.place(x=window[0]//2, y=430, anchor=tk.CENTER)

# Bouton pour voir le dataframe raffiné
processed_label = tk.Label(root, text="View the processed DataFrame", font=("Helvetica", 12, "bold"))
processed_label.place(x=window[0]//2+400, y=400, anchor=tk.CENTER)

processed_button = tk.Button(root, text="SHOW PROCESSED DATAFRAME", width=30, bg="orange", font=("Helvetica", 12, "bold"), command=open_processed_dataframe_window)
processed_button.place(x=window[0]//2+400, y=430, anchor=tk.CENTER)

check_file_presence()

root.mainloop()