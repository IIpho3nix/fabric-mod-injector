import os
import json
import shutil
from zipfile import ZipFile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tempfile import TemporaryDirectory

def open_file_dialog(entry):
    file_path = filedialog.askopenfilename(filetypes=[("JAR files", "*.jar")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)
        
def on_closing():
    root.destroy()
        

def inject():
    target_jar_path = jar_target_entry.get()
    inject_jar_path = jar_inject_entry.get()

    with TemporaryDirectory() as temp_dir:
        temp_jar_path = os.path.join(temp_dir, "temp.jar")

        with ZipFile(target_jar_path, 'r') as target_jar:
            target_jar.extractall(temp_dir)

        fabric_mod_json_path = os.path.join(temp_dir, 'fabric.mod.json')
        meta_inf_path = os.path.join(temp_dir, 'META-INF')
        jars_folder_path = os.path.join(meta_inf_path, 'jars')

        if not os.path.isfile(fabric_mod_json_path) or not os.path.exists(meta_inf_path):
            messagebox.showerror("Error", "Selected JAR file is not a Fabric mod.")
            return

        with open(fabric_mod_json_path, 'r', encoding='utf-8') as fabric_mod_file:
            fabric_mod_data = json.load(fabric_mod_file)

        if 'jars' not in fabric_mod_data:
            fabric_mod_data['jars'] = []

        injected_jar_name = os.path.basename(inject_jar_path)
        fabric_mod_data['jars'].append({"file": f"META-INF/jars/{injected_jar_name}"})

        with open(fabric_mod_json_path, 'w', encoding='utf-8') as fabric_mod_file:
            json.dump(fabric_mod_data, fabric_mod_file, indent=2)

        if not os.path.exists(jars_folder_path):
            os.makedirs(jars_folder_path)

        injected_jar_destination = os.path.join(jars_folder_path, injected_jar_name)
        shutil.copy(inject_jar_path, injected_jar_destination)

        modified_jar_path = target_jar_path.replace('.jar', '_injected.jar')
        with ZipFile(modified_jar_path, 'w') as modified_jar:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    modified_jar.write(file_path, arcname)

    messagebox.showinfo("Success", "Successfully injected JAR.")
        
root = tk.Tk()
root.iconbitmap("icon.ico")
root.title("Fabric JIJ Injector")
root.geometry("200x215")
root.resizable(False,False)

style = ttk.Style()
style.configure("TButton", padding=(10, 5))
style.configure("TLabel", padding=(0, 5))

jar_target_label = ttk.Label(root, text="Select JAR file to inject into:")
jar_target_label.pack()
jar_target_entry = ttk.Entry(root)
jar_target_entry.pack()
browse_target = ttk.Button(root, text="Browse", command=lambda : open_file_dialog(jar_target_entry))
browse_target.pack()

jar_inject_label = ttk.Label(root, text="Select JAR file to Inject:")
jar_inject_label.pack()
jar_inject_entry = ttk.Entry(root)
jar_inject_entry.pack()
browse_inject = ttk.Button(root, text="Browse", command=lambda : open_file_dialog(jar_inject_entry))
browse_inject.pack()

inject_button = ttk.Button(root, text="Inject", command=inject)
inject_button.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()