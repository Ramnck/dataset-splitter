import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import os
import shutil

class SegmentationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Segmentation NN SFT Sample Sorter")
        self.configure(bg="#2e2e2e")

        # Data
        self.image_folder = ""
        self.label_folder = ""
        self.output_folder = ""
        self.image_files = []
        self.total_samples = 0
        self.target_count = 0
        self.marked = set()
        self.current_idx = 0

        # UI vars
        self.image_entry_var = tk.StringVar()
        self.label_entry_var = tk.StringVar()
        self.output_entry_var = tk.StringVar()
        self.percent_var = tk.DoubleVar(value=0)
        self.number_var = tk.IntVar(value=0)

        # Build UI
        self.setup_screen1()

    def setup_screen1(self):
        self.screen1 = tk.Frame(self, bg="#2e2e2e")
        self.screen1.pack(fill="both", expand=True)
        
        # Grid for adaptive preview
        for r in range(4):
            self.screen1.grid_rowconfigure(r, weight=1)
        self.screen1.grid_columnconfigure(3, weight=1)

        # Folder selectors
        folders = [
            ("Images Folder:", self.image_entry_var, self.select_image_folder),
            ("Labels Folder:", self.label_entry_var, self.select_label_folder),
            ("Output Folder:", self.output_entry_var, self.select_output_folder)
        ]
        for i, (txt, var, cmd) in enumerate(folders):
            tk.Label(self.screen1, text=txt, bg="#2e2e2e", fg="white").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            tk.Entry(self.screen1, textvariable=var, width=50).grid(row=i, column=1, padx=5, pady=5)
            tk.Button(self.screen1, text="Browse", command=cmd).grid(row=i, column=2, padx=5, pady=5)

        # Preview canvas
        self.preview_canvas = tk.Canvas(self.screen1, bg="black", bd=0, highlightthickness=0)
        self.preview_canvas.grid(row=0, column=3, rowspan=4, sticky="nsew", padx=10, pady=10)
        self.preview_canvas.bind("<Configure>", lambda e: self.load_preview())

        # Split controls
        row = 4
        tk.Label(self.screen1, text="High-quality split (%):", bg="#2e2e2e", fg="white").grid(row=row, column=0, sticky="e", padx=5)
        self.scale = tk.Scale(self.screen1, from_=0, to=100, orient="horizontal", variable=self.percent_var)
        self.scale.grid(row=row, column=1, columnspan=2, sticky="we", padx=5)
        row += 1
        tk.Label(self.screen1, text="Number of samples:", bg="#2e2e2e", fg="white").grid(row=row, column=0, sticky="e", padx=5)
        tk.Entry(self.screen1, textvariable=self.number_var, width=10).grid(row=row, column=1, sticky="w")

        # Sync
        self.percent_var.trace_add('write', self.update_number_from_percent)
        self.number_var.trace_add('write', self.update_percent_from_number)

        # Start
        tk.Button(self.screen1, text="Start Sorting", command=self.start_sorting).grid(row=row+1, column=1, pady=10)

    def select_image_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_folder = folder
            self.image_entry_var.set(folder)
            self.load_preview()

    def select_label_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.label_folder = folder
            self.label_entry_var.set(folder)
            self.load_preview()

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_entry_var.set(folder)

    def load_preview(self):
        if not (self.image_folder and self.label_folder): return
        imgs = sorted(f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png','.jpg','.jpeg')))
        if not imgs: return
        self.total_samples = len(imgs)
        self.update_number_from_percent()
        self.update_percent_from_number()
        self._draw_and_scale(imgs[0], self.preview_canvas)

    def _draw_and_scale(self, img_name, canvas):
        img_path = os.path.join(self.image_folder, img_name)
        lbl_path = os.path.join(self.label_folder, os.path.splitext(img_name)[0] + '.txt')
        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)
        w, h = img.size
        if os.path.exists(lbl_path):
            for line in open(lbl_path):
                parts = line.strip().split()
                if len(parts) == 5:
                    _, x, y, bw, bh = map(float, parts)
                    x1, y1 = (x - bw/2) * w, (y - bh/2) * h
                    x2, y2 = (x + bw/2) * w, (y + bh/2) * h
                    draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        cw, ch = canvas.winfo_width(), canvas.winfo_height()
        if cw > 1 and ch > 1:
            scale = min(cw / w, ch / h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        tkimg = ImageTk.PhotoImage(img)
        canvas.delete("all")
        canvas.create_image((cw - img.width) // 2, (ch - img.height) // 2, anchor="nw", image=tkimg)
        canvas.image = tkimg

    def update_number_from_percent(self, *_):
        if self.total_samples:
            self.number_var.set(int(self.percent_var.get() / 100 * self.total_samples))

    def update_percent_from_number(self, *_):
        if self.total_samples:
            try:
                self.percent_var.set(self.number_var.get() / self.total_samples * 100)
            except:
                pass

    def start_sorting(self):
        if not (self.image_folder and self.label_folder and self.output_folder):
            messagebox.showerror("Error", "Set all folders first.")
            return
        self.image_files = sorted(f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png','.jpg','.jpeg')))
        self.total_samples = len(self.image_files)
        if not self.total_samples:
            messagebox.showerror("Error", "No images found.")
            return
        self.target_count = self.number_var.get()
        self.screen1.pack_forget()
        self.setup_screen2()

    def setup_screen2(self):
        self.screen2 = tk.Frame(self, bg="#2e2e2e")
        self.screen2.pack(fill="both", expand=True)
        self.screen2.grid_rowconfigure(0, weight=1)
        for c in range(4): self.screen2.grid_columnconfigure(c, weight=1)

        self.canvas = tk.Canvas(self.screen2, bg="black", bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda e: self.show_image())

        # Image index label
        self.img_lbl = tk.Label(self.screen2, text="", bg="#2e2e2e", fg="white")
        self.img_lbl.grid(row=1, column=0, columnspan=4)

        # Control buttons
        self.prev_btn = tk.Button(self.screen2, text="Previous", command=self.prev_image)
        self.prev_btn.grid(row=2, column=0, sticky="we", padx=5, pady=5)
        self.action_btn = tk.Button(self.screen2, text="", command=self.toggle_mark)
        self.action_btn.grid(row=2, column=1, sticky="we", padx=5, pady=5)
        self.next_btn = tk.Button(self.screen2, text="Next", command=self.next_image)
        self.next_btn.grid(row=2, column=2, sticky="we", padx=5, pady=5)
        self.finish_btn = tk.Button(self.screen2, text="Finish", command=self.finish_early)
        self.finish_btn.grid(row=2, column=3, sticky="we", padx=5, pady=5)

        # Bind shortcuts
        self.bind("<a>", lambda e: self.prev_image())
        self.bind("<s>", lambda e: self.toggle_mark())
        self.bind("<d>", lambda e: self.next_image())
        self.bind("<f>", lambda e: self.finish_early())

        style = ttk.Style()
        style.theme_use('default')
        style.configure("red.Horizontal.TProgressbar", troughcolor='#555555', background='#F14C42')
        self.progress = ttk.Progressbar(self.screen2, style="red.Horizontal.TProgressbar",
                                        orient="horizontal", mode='determinate', maximum=self.target_count)
        self.progress.grid(row=3, column=0, columnspan=4, sticky="we", padx=10, pady=5)
        self.progress_lbl = tk.Label(self.screen2, text="", bg="#2e2e2e", fg="white")
        self.progress_lbl.grid(row=4, column=0, columnspan=4)

        self.update_ui()

    def show_image(self):
        if not self.image_files: return
        self._draw_and_scale(self.image_files[self.current_idx], self.canvas)

    def toggle_mark(self):
        if self.current_idx in self.marked:
            self.marked.remove(self.current_idx)
        else:
            self.marked.add(self.current_idx)
            self.check_target()
        self.next_image()

    def next_image(self):
        if self.current_idx < self.total_samples - 1:
            self.current_idx += 1
        self.update_ui()

    def prev_image(self):
        if self.current_idx > 0:
            self.current_idx -= 1
        self.update_ui()

    def finish_early(self):
        if messagebox.askyesno("Finish early", "Are you sure you want to finish sorting now?"):
            self.save_and_exit()

    def update_ui(self):
        # redraw image
        self.show_image()
        # update image index label
        self.img_lbl.config(text=f"Image {self.current_idx+1}/{self.total_samples}")
        # update action button
        if self.current_idx in self.marked:
            self.action_btn.config(text="Unmark", bg="#aa0000")
        else:
            self.action_btn.config(text="Mark", bg="#00aa00")
        # update progress
        cnt = len(self.marked)
        self.progress['value'] = cnt
        self.progress_lbl.config(text=f"{cnt}/{self.target_count} found")

    def check_target(self):
        if len(self.marked) >= self.target_count:
            if messagebox.askyesno("Target reached", "High-quality target reached. Stop? "):
                self.save_and_exit()

    def save_and_exit(self):
        base = self.output_folder
        paths = {True: ('test/images', 'test/labels'), False: ('train/images', 'train/labels')}
        for idx, name in enumerate(self.image_files):
            mark = idx in self.marked
            img_src = os.path.join(self.image_folder, name)
            lbl_src = os.path.join(self.label_folder, os.path.splitext(name)[0] + '.txt')
            img_dst = os.path.join(base, paths[mark][0], name)
            lbl_dst = os.path.join(base, paths[mark][1], os.path.basename(lbl_src))
            os.makedirs(os.path.dirname(img_dst), exist_ok=True)
            os.makedirs(os.path.dirname(lbl_dst), exist_ok=True)
            shutil.copy(img_src, img_dst)
            if os.path.exists(lbl_src): shutil.copy(lbl_src, lbl_dst)
        messagebox.showinfo("Done", "Samples split and copied.")
        self.quit()

if __name__ == "__main__":
    SegmentationApp().mainloop()
