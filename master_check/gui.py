"""Desktop window: pick masters, read the report, save it as HTML or JSON."""
import os
import queue
import threading

from . import APP_NAME, __version__, report
from .cli import collect, run

INTRO = (
    "Add one or more finished masters (WAV, AIFF, FLAC, MP3).\n\n"
    "For each file you get integrated loudness, true peak and LRA, what Spotify,\n"
    "Apple Music, YouTube and the other platforms will do to its volume, and the\n"
    "delivery problems that get a release rejected.\n"
)


def main():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext

    root = tk.Tk()
    root.title("%s %s" % (APP_NAME, __version__))
    root.geometry("900x640")
    state = {"results": [], "busy": False}
    events = queue.Queue()

    tk.Label(root, text=APP_NAME, font=("Helvetica", 18, "bold")).pack(pady=(14, 0))
    tk.Label(root, text="Release QC for finished masters").pack(pady=(0, 8))

    bar = tk.Frame(root)
    bar.pack(fill="x", padx=12)
    status = tk.Label(root, anchor="w", fg="#555")
    out = scrolledtext.ScrolledText(root, font=("Courier", 11), wrap="none")
    for level, color in (("fail", "#b00020"), ("warn", "#a15c00"), ("ok", "#1b7f3b")):
        out.tag_configure(level, foreground=color)

    def show(text_value):
        out.configure(state="normal")
        out.delete("1.0", "end")
        for line in text_value.split("\n"):
            tag = None
            for level, label in report.LABEL.items():
                if level != "info" and (" %s " % label) in (" " + line + " "):
                    tag = level
            out.insert("end", line + "\n", tag)
        out.configure(state="disabled")

    def start(paths):
        if state["busy"] or not paths:
            return
        files = collect(paths)
        if not files:
            messagebox.showinfo(APP_NAME, "No audio files found there.")
            return
        state["busy"] = True

        def work():
            res = run(files, progress=lambda n, total, p: events.put(
                ("progress", "Measuring %d of %d: %s" % (n + 1, total, os.path.basename(p)))))
            events.put(("done", res))

        threading.Thread(target=work, daemon=True).start()

    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == "progress":
                    status.configure(text=value)
                else:
                    state["busy"] = False
                    state["results"] = value
                    fails = sum(r["status"] == "fail" for r in value)
                    status.configure(text="%d file(s) checked, %d with problems to fix."
                                     % (len(value), fails))
                    show(report.text(value))
        except queue.Empty:
            pass
        root.after(150, poll)

    def add_files():
        start(list(filedialog.askopenfilenames(
            title="Choose masters",
            filetypes=[("Audio", "*.wav *.wave *.aif *.aiff *.aifc *.flac *.mp3 *.ogg"),
                       ("All files", "*.*")])))

    def add_folder():
        folder = filedialog.askdirectory(title="Folder with masters")
        if folder:
            start([folder])

    def save(kind):
        if not state["results"]:
            messagebox.showinfo(APP_NAME, "Check a master first.")
            return
        ext = ".html" if kind == "html" else ".json"
        path = filedialog.asksaveasfilename(defaultextension=ext,
                                            initialfile="master-check-report" + ext)
        if not path:
            return
        body = report.to_html(state["results"]) if kind == "html" else report.to_json(
            state["results"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        status.configure(text="Saved %s" % path)

    tk.Button(bar, text="Check files...", width=16, command=add_files).pack(side="left", padx=4)
    tk.Button(bar, text="Check a folder...", width=16, command=add_folder).pack(side="left",
                                                                                padx=4)
    tk.Button(bar, text="Save JSON...", width=14, command=lambda: save("json")).pack(
        side="right", padx=4)
    tk.Button(bar, text="Save HTML report...", width=18, command=lambda: save("html")).pack(
        side="right", padx=4)
    status.pack(fill="x", padx=16, pady=(8, 0))
    out.pack(fill="both", expand=True, padx=12, pady=12)
    show(INTRO)
    poll()
    root.mainloop()
