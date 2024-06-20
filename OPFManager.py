import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk

class OPFManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("800x600")

        self.opfcont_path = r"path"
        self.opfmatch_path = r"path"

        # Configure les styles
        self.configure_styles()

        # Création des cadres pour chaque fichier d'affichage et de contrôle
        self.opfcont_frame = tk.Frame(root, padx=10, pady=10, bg="#f0f0f0")
        self.opfcont_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.opfmatch_frame = tk.Frame(root, padx=10, pady=10, bg="#f0f0f0")
        self.opfmatch_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_file_display(self.opfcont_frame, "OpfCont", self.opfcont_path)
        self.create_file_display(self.opfmatch_frame, "OpfMatch", self.opfmatch_path)

    def configure_styles(self):
        self.root.configure(bg="#ffffff")

        # Style pour les boutons
        self.button_style = ttk.Style()
        self.button_style.configure('Padded.TButton', padding=(10, 5), font=('Arial', 12))

        # Style pour les entrées de texte
        self.entry_style = ttk.Style()
        self.entry_style.configure('Custom.TEntry', foreground='#333333', font=('Arial', 12))

    def create_file_display(self, frame, file_label, file_path):
        label = tk.Label(frame, text=file_label, font=('Arial', 16, 'bold'), bg="#f0f0f0", fg="#333333")
        label.pack(pady=(0, 10))

        text_frame = tk.Frame(frame, bg="#ffffff")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, state=tk.DISABLED, wrap=tk.WORD,
                              bg="#ffffff", fg="#333333", font=('Arial', 12))
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        setattr(self, f"{file_label.lower().replace(' ', '_')}_text", text_widget)

        button_frame = tk.Frame(frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(20, 0))

        add_word_button = ttk.Button(button_frame, text="Add Word", command=lambda: self.add_word(file_label),
                                    style='Padded.TButton')
        add_word_button.pack(side=tk.LEFT, padx=10)

        add_list_button = ttk.Button(button_frame, text="Add List", command=lambda: self.add_list(file_label),
                                    style='Padded.TButton')
        add_list_button.pack(side=tk.LEFT, padx=10)

        save_file_button = ttk.Button(button_frame, text="Save File", command=lambda: self.save_file(file_label),
                                     style='Padded.TButton')
        save_file_button.pack(side=tk.LEFT, padx=10)

        search_button = ttk.Button(button_frame, text="Search", command=lambda: self.search_word(file_label),
                                  style='Padded.TButton')
        search_button.pack(side=tk.LEFT, padx=10)

        self.load_file_content(file_path, text_widget)

    def load_file_content(self, file_path, text_widget):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file {file_path}: {str(e)}")

    def save_file(self, file_label):
        file_path = getattr(self, f"{file_label.lower()}_path", None)
        if file_path:
            text_widget = getattr(self, f"{file_label.lower()}_text")
            content = text_widget.get(1.0, tk.END)
            with open(file_path, 'w') as file:
                file.write(content)
            messagebox.showinfo("Info", f"{file_label} saved successfully!")
        else:
            messagebox.showwarning("Warning", "File path not set. Save operation failed.")

    def add_word(self, file_label):
        word = simpledialog.askstring("Input", f"Enter a word to add to {file_label}")
        if word:
            text_widget = getattr(self, f"{file_label.lower().replace(' ', '_')}_text")
            current_content = text_widget.get(1.0, tk.END).splitlines()
            if word not in current_content:
                current_content.append(word)
                current_content = sorted(set(current_content))
                self.update_text_widget(text_widget, current_content)
            else:
                messagebox.showwarning("Warning", "Word already exists in the file!")

    def add_list(self, file_label):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                new_words = file.read().splitlines()
            text_widget = getattr(self, f"{file_label.lower().replace(' ', '_')}_text")
            current_content = text_widget.get(1.0, tk.END).splitlines()
            
            existing_words = [word for word in new_words if word in current_content]
            new_unique_words = sorted(set(new_words) - set(current_content))
            
            if existing_words and new_unique_words:
                messagebox.showwarning("Warning", f"{len(existing_words)} words already exist in {file_label}. {len(new_unique_words)} new words added.")
            elif existing_words:
                messagebox.showwarning("Warning", f"All {len(existing_words)} words already exist in {file_label}. No new words added.")
            elif new_unique_words:
                messagebox.showinfo("Info", f"{len(new_unique_words)} new words added to {file_label}.")
            
            unique_words = sorted(set(current_content + new_unique_words))
            self.update_text_widget(text_widget, unique_words)

    def search_word(self, file_label):
        word = simpledialog.askstring("Search", f"Enter a word to search in {file_label}")
        if word:
            text_widget = getattr(self, f"{file_label.lower().replace(' ', '_')}_text")
            text_widget.tag_remove('found', '1.0', tk.END)
            start_idx = '1.0'
            found_indices = []
            while True:
                start_idx = text_widget.search(word, start_idx, stopindex=tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(word)}c"
                text_widget.tag_add('found', start_idx, end_idx)
                found_indices.append(start_idx)
                start_idx = end_idx

            if found_indices:
                text_widget.tag_config('found', background='yellow')
                text_widget.see('found.first')
                self.show_navigation_popup(file_label, found_indices)
            else:
                messagebox.showinfo("Not Found", f"'{word}' not found in {file_label}")

    def show_navigation_popup(self, file_label, found_indices):
        popup = tk.Toplevel(self.root)
        popup.title(f"Navigation for {file_label}")
        popup.configure(bg="#ffffff")
        
        label = tk.Label(popup, text=f"{len(found_indices)} occurrences found for the search term.", font=('Arial', 12), bg="#ffffff", fg="#333333")
        label.pack(padx=10, pady=10)

        navigation_frame = tk.Frame(popup, bg="#ffffff")
        navigation_frame.pack(padx=10, pady=10)

        current_index = tk.IntVar()
        current_index.set(0)

        def show_current_occurrence():
            text_widget = getattr(self, f"{file_label.lower().replace(' ', '_')}_text")
            text_widget.see(found_indices[current_index.get()])
        
        previous_button = ttk.Button(navigation_frame, text="Previous", command=lambda: change_index(-1), style='Padded.TButton')
        previous_button.pack(side=tk.LEFT, padx=10)

        next_button = ttk.Button(navigation_frame, text="Next", command=lambda: change_index(1), style='Padded.TButton')
        next_button.pack(side=tk.LEFT, padx=10)

        def change_index(delta):
            new_index = current_index.get() + delta
            if 0 <= new_index < len(found_indices):
                current_index.set(new_index)
                show_current_occurrence()

        show_current_occurrence()

    def update_text_widget(self, text_widget, content_list):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, '\n'.join(content_list) + '\n')
        text_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = OPFManager(root)
    root.mainloop()
