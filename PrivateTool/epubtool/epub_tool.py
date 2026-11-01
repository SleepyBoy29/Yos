"""
EPUB Tool - batch rename + remove specific words inside EPUB content.
Uses only the Python standard library (no pip install needed).
"""
import os
import re
import shutil
import threading
import queue
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

TEXT_EXT = (".xhtml", ".html", ".htm", ".xml", ".ncx", ".opf")


# ---------------------------------------------------------------- logic
def clean_filename(name, prefix, use_regex, words, apply_words):
    base, ext = os.path.splitext(name)
    if prefix:
        pattern = prefix if use_regex else re.escape(prefix)
        base = re.sub(r"^(?:" + pattern + r")", "", base, count=1, flags=re.I)
    if apply_words:
        for w in words:
            base = re.sub(re.escape(w), "", base, flags=re.I)
    base = re.sub(r"\s{2,}", " ", base).strip(" -_.")
    return (base or "untitled") + ext


def unique_path(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(f"{base} ({i}){ext}"):
        i += 1
    return f"{base} ({i}){ext}"


def clean_text(text, words, remove_para):
    """Remove words only in text nodes (not inside tags/attributes) so links stay intact."""
    total = 0
    pats = [re.compile(re.escape(w), re.I) for w in words]

    if remove_para:
        def para_fn(m):
            nonlocal total
            plain = re.sub(r"<[^>]+>", "", m.group(0))
            if any(p.search(plain) for p in pats):
                total += 1
                return ""
            return m.group(0)
        text = re.sub(r"<p\b[^>]*>.*?</p>", para_fn, text, flags=re.S | re.I)

    parts = re.split(r"(<[^>]+>)", text)
    for i in range(0, len(parts), 2):  # even indexes = plain text
        for p in pats:
            parts[i], n = p.subn("", parts[i])
            total += n
    return "".join(parts), total


def clean_epub(src, dst, words, remove_para):
    total = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.lower().endswith(TEXT_EXT):
                try:
                    text = data.decode("utf-8")
                    text, n = clean_text(text, words, remove_para)
                    total += n
                    data = text.encode("utf-8")
                except UnicodeDecodeError:
                    pass
            # mimetype must be stored uncompressed (EPUB requirement)
            comp = zipfile.ZIP_STORED if item.filename == "mimetype" else zipfile.ZIP_DEFLATED
            zout.writestr(item.filename, data, compress_type=comp)
    return total


def process_folder(folder, prefix, use_regex, words, remove_para,
                   apply_words_name, use_subfolder, log):
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".epub"))
    if not files:
        log("No .epub files found in this folder.")
        return
    out_dir = os.path.join(folder, "output") if use_subfolder else folder
    os.makedirs(out_dir, exist_ok=True)
    log(f"Found {len(files)} EPUB file(s).\n")

    for f in files:
        src = os.path.join(folder, f)
        new_name = clean_filename(f, prefix, use_regex, words, apply_words_name)
        dst = os.path.join(out_dir, new_name)
        in_place = os.path.abspath(dst) == os.path.abspath(src)
        if not in_place:
            dst = unique_path(dst)
        try:
            if words:
                tmp = dst + ".tmp"
                n = clean_epub(src, tmp, words, remove_para)
                if not use_subfolder:
                    os.remove(src)
                os.replace(tmp, dst)
                log(f"OK  {f}\n    -> {os.path.basename(dst)}  ({n} removed)")
            else:
                if in_place:
                    log(f"--  {f} (unchanged)")
                elif use_subfolder:
                    shutil.copy2(src, dst)
                    log(f"OK  {f}\n    -> {os.path.basename(dst)}")
                else:
                    os.rename(src, dst)
                    log(f"OK  {f}\n    -> {os.path.basename(dst)}")
        except Exception as e:
            log(f"FAILED {f}: {e}")
    log("\nDone.")


# ---------------------------------------------------------------- GUI
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EPUB Tool")
        self.geometry("720x640")
        self.q = queue.Queue()

        pad = {"padx": 10, "pady": 4}
        self.folder = tk.StringVar()
        self.prefix = tk.StringVar()
        self.use_regex = tk.BooleanVar(value=False)
        self.remove_para = tk.BooleanVar(value=False)
        self.apply_name = tk.BooleanVar(value=True)
        self.subfolder = tk.BooleanVar(value=True)

        ttk.Label(self, text="Folder containing EPUBs:").pack(anchor="w", **pad)
        row = ttk.Frame(self)
        row.pack(fill="x", **pad)
        ttk.Entry(row, textvariable=self.folder).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse...", command=self.pick).pack(side="left", padx=(6, 0))

        ttk.Label(self, text="Text at the start of the filename to remove (e.g. [Novel] ):").pack(anchor="w", **pad)
        ttk.Entry(self, textvariable=self.prefix).pack(fill="x", **pad)
        ttk.Checkbutton(self, text="Use regex (e.g. \\d+\\s*-\\s* for '123 - ')",
                        variable=self.use_regex).pack(anchor="w", **pad)

        ttk.Label(self, text="Words to remove from EPUB content (one per line, leave empty to skip):").pack(anchor="w", **pad)
        self.words = scrolledtext.ScrolledText(self, height=5)
        self.words.pack(fill="x", **pad)
        self.words.insert("1.0", "kucingterbang")

        ttk.Checkbutton(self, text="Remove the whole <p> paragraph containing these words (good for one-line watermarks)",
                        variable=self.remove_para).pack(anchor="w", **pad)
        ttk.Checkbutton(self, text="Also remove these words from the filename",
                        variable=self.apply_name).pack(anchor="w", **pad)
        ttk.Checkbutton(self, text="Save results to 'output' subfolder (originals stay safe). Off = overwrite originals",
                        variable=self.subfolder).pack(anchor="w", **pad)

        row2 = ttk.Frame(self)
        row2.pack(fill="x", **pad)
        ttk.Button(row2, text="Preview Names", command=self.preview).pack(side="left")
        self.run_btn = ttk.Button(row2, text="Start", command=self.run)
        self.run_btn.pack(side="left", padx=6)

        self.log_box = scrolledtext.ScrolledText(self, state="disabled", height=14)
        self.log_box.pack(fill="both", expand=True, **pad)
        self.after(100, self.drain)

    def pick(self):
        d = filedialog.askdirectory()
        if d:
            self.folder.set(d)

    def get_words(self):
        return [w.strip() for w in self.words.get("1.0", "end").splitlines() if w.strip()]

    def log(self, msg):
        self.q.put(msg)

    def drain(self):
        try:
            while True:
                msg = self.q.get_nowait()
                self.log_box.config(state="normal")
                self.log_box.insert("end", msg + "\n")
                self.log_box.see("end")
                self.log_box.config(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self.drain)

    def check_folder(self):
        f = self.folder.get()
        if not os.path.isdir(f):
            messagebox.showwarning("EPUB Tool", "Please choose a folder first.")
            return None
        return f

    def preview(self):
        f = self.check_folder()
        if not f:
            return
        try:
            words = self.get_words()
            for name in sorted(x for x in os.listdir(f) if x.lower().endswith(".epub")):
                new = clean_filename(name, self.prefix.get(), self.use_regex.get(),
                                     words, self.apply_name.get())
                self.log(f"{name}\n  -> {new}")
        except re.error as e:
            messagebox.showerror("Invalid regex", str(e))

    def run(self):
        f = self.check_folder()
        if not f:
            return
        if not self.subfolder.get() and not messagebox.askyesno(
                "Confirm", "Original files will be OVERWRITTEN. Continue?"):
            return
        words = self.get_words()
        args = (f, self.prefix.get(), self.use_regex.get(), words,
                self.remove_para.get(), self.apply_name.get(),
                self.subfolder.get(), self.log)
        self.run_btn.config(state="disabled")

        def work():
            try:
                process_folder(*args)
            except Exception as e:
                self.log(f"ERROR: {e}")
            finally:
                self.after(0, lambda: self.run_btn.config(state="normal"))

        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
