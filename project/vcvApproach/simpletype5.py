import tkinter as tk
import math
from dataclasses import dataclass, field

# --- constants ---------------------------------------------------------------

PORT_R = 7
CANVAS_W, CANVAS_H = 1100, 680
COL_BG = "#0f0f14"
COL_PANEL = "#17171b"
COL_CARD = "#1f1f24"
COL_STROKE = "#7a7a88"
COL_TEXT = "#e6e6f0"
COL_SUBTLE = "#b8bec9"
COL_IN = "#ff7676"
COL_OUT = "#44d17a"
COL_WIRE = "#39d5ff"
COL_TEMP = "#f5d90a"

# --- utils -------------------------------------------------------------------


def within_circle(x, y, cx, cy, r=PORT_R + 2):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


# --- dataflow ----------------------------------------------------------------


@dataclass
class Port:
    module: "Module"
    name: str
    kind: str  # "in" or "out"
    relx: int
    rely: int
    value: float = 0.0
    id_circle: int | None = None
    id_label: int | None = None
    id_value: int | None = None

    def pos(self):
        return self.module.x + self.relx, self.module.y + self.rely


class Cable:
    def __init__(self, canvas, src: Port, dst: Port):
        self.canvas, self.src, self.dst = canvas, src, dst
        self.id_line = canvas.create_line(
            *self._points(),
            smooth=True,
            splinesteps=24,
            width=3,
            fill=COL_WIRE,
            capstyle="round",
        )
        canvas.tag_bind(self.id_line, "<Button-3>", self._remove)

    def _points(self):
        x1, y1 = self.src.pos()
        x2, y2 = self.dst.pos()
        mx = (x1 + x2) / 2
        return (x1, y1, mx, y1, mx, y2, x2, y2)

    def redraw(self):
        self.canvas.coords(self.id_line, *self._points())

    def _remove(self, _=None):
        try:
            self.canvas.delete(self.id_line)
        except tk.TclError:
            pass
        app = self.canvas.master.app
        if self in app.cables:
            app.cables.remove(self)


class Module:
    def __init__(
        self, canvas, x, y, title="Module", inputs=("in",), outputs=("out",), code=""
    ):
        self.canvas, self.x, self.y = canvas, x, y
        self.w, self.h = 210, 190
        self.title = title
        self.inputs_def, self.outputs_def = list(inputs), list(outputs)
        self.code = code or (
            f"{self.outputs_def[0]} = "
            f"{' + '.join(self.inputs_def) if self.inputs_def else '0.0'}"
            if self.outputs_def
            else "# define outputs here"
        )
        self.id_rect = self.id_title = None
        self.inputs: list[Port] = []
        self.outputs: list[Port] = []
        self._draw()

    # --- drawing -------------------------------------------------------------

    def _draw(self):
        if not self.id_rect:
            self.id_rect = self.canvas.create_rectangle(
                self.x,
                self.y,
                self.x + self.w,
                self.y + self.h,
                fill=COL_CARD,
                outline=COL_STROKE,
                width=2,
                tags=("module",),
            )
        else:
            self.canvas.coords(
                self.id_rect, self.x, self.y, self.x + self.w, self.y + self.h
            )

        if not self.id_title:
            self.id_title = self.canvas.create_text(
                self.x + self.w / 2,
                self.y + 16,
                text=self.title,
                fill="white",
                font=("Arial", 12, "bold"),
            )
        else:
            self.canvas.coords(self.id_title, self.x + self.w / 2, self.y + 16)
            self.canvas.itemconfigure(self.id_title, text=self.title)

        for plist in (self.inputs, self.outputs):
            for p in plist:
                for item in (p.id_circle, p.id_label, p.id_value):
                    if item:
                        self.canvas.delete(item)

        self.inputs = self._make_ports(self.inputs_def, side="left")
        self.outputs = self._make_ports(self.outputs_def, side="right")

    def _make_ports(self, names, side="left"):
        ports, top, n = [], 44, max(1, len(names))
        gap = (self.h - top - 16) / n
        anchor = "w" if side == "left" else "e"
        x = 18 if side == "left" else self.w - 18
        kind = "in" if side == "left" else "out"
        color = COL_IN if kind == "in" else COL_OUT

        for i, name in enumerate(names):
            p = Port(self, name, kind, x, top + gap * i + 12)
            px, py = p.pos()
            p.id_circle = self.canvas.create_oval(
                px - PORT_R,
                py - PORT_R,
                px + PORT_R,
                py + PORT_R,
                fill=color,
                outline="#000",
                width=1,
                tags=("port", kind),
            )
            label_x = px + 13 if side == "left" else px - 13
            p.id_label = self.canvas.create_text(
                label_x, py, text=name, fill=COL_TEXT, font=("Arial", 9), anchor=anchor
            )
            p.id_value = self.canvas.create_text(
                px, py - 15, text="0.0", fill="#b5e3ff", font=("Arial", 8)
            )
            if kind == "out":
                self.canvas.tag_bind(
                    p.id_circle, "<Button-1>", lambda e, port=p: self._start_wire(port)
                )
            ports.append(p)
        return ports

    def _start_wire(self, port: Port):
        self.canvas.master.app.begin_wire_drag(port)

    # --- compute -------------------------------------------------------------

    def evaluate(self, inputs_dict: dict[str, float]) -> dict[str, float]:
        env = {k: float(v) for k, v in inputs_dict.items()}
        try:
            exec(self.code, {"__builtins__": {}, "math": math}, env)
        except Exception:
            pass
        return {name: float(env.get(name, 0.0)) for name in self.outputs_def}

    # --- editor --------------------------------------------------------------

    def open_editor(self):
        dlg = tk.Toplevel(self.canvas.master)
        dlg.title(f"Define Math • {self.title}")
        dlg.configure(bg="#26262c")
        dlg.geometry("640x520")
        dlg.grab_set()

        mklabel = lambda r, c, t: tk.Label(dlg, text=t, fg="white", bg="#26262c").grid(
            row=r, column=c, sticky="w", padx=10, pady=4
        )
        mklabel(0, 0, "Title")
        e_title = tk.Entry(dlg, width=30)
        e_title.insert(0, self.title)
        e_title.grid(row=0, column=1, padx=10, pady=(12, 4), sticky="w")
        mklabel(1, 0, "Inputs (comma-separated)")
        e_in = tk.Entry(dlg, width=50)
        e_in.insert(0, ", ".join(self.inputs_def))
        e_in.grid(row=1, column=1, padx=10, pady=4, sticky="we")
        mklabel(2, 0, "Outputs (comma-separated)")
        e_out = tk.Entry(dlg, width=50)
        e_out.insert(0, ", ".join(self.outputs_def))
        e_out.grid(row=2, column=1, padx=10, pady=4, sticky="we")
        mklabel(3, 0, "Python code (assign outputs)")
        txt = tk.Text(
            dlg,
            width=70,
            height=18,
            bg="#1e1e22",
            fg="#eaeaf0",
            insertbackground="white",
        )
        txt.insert(
            "1.0",
            self.code.strip()
            or "# Example:\n# salary = 0.6 * worker_output\n# taxes  = 0.2 * max(0, revenues + subsidies - salary)\n",
        )
        txt.grid(row=3, column=1, padx=10, pady=4, sticky="nsew")
        dlg.grid_columnconfigure(1, weight=1)
        dlg.grid_rowconfigure(3, weight=1)

        def save():
            self._remove_cables_touching_ports()
            self.title = e_title.get().strip() or "Module"
            self.inputs_def = [
                s.strip() for s in e_in.get().split(",") if s.strip()
            ] or ["in"]
            self.outputs_def = [
                s.strip() for s in e_out.get().split(",") if s.strip()
            ] or ["out"]
            self.code = txt.get("1.0", "end-1c") or "# define outputs here"
            self._draw()
            dlg.destroy()

        tk.Button(dlg, text="Save", command=save).grid(
            row=4, column=0, columnspan=2, pady=10
        )

    def _remove_cables_touching_ports(self):
        app = self.canvas.master.app
        for c in [
            c for c in app.cables if c.src.module is self or c.dst.module is self
        ]:
            c._remove()


# --- app / platform ----------------------------------------------------------


@dataclass
class ModeSpec:
    name: str
    tooltip: str
    active: bool = False
    button: tk.Button | None = field(default=None, compare=False)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Economic Patch Platform — mini")
        self.toolbar = tk.Frame(root, bg=COL_PANEL)
        self.toolbar.pack(side="top", fill="x")
        self.status = tk.Label(root, text="Ready", anchor="w", bg=COL_BG, fg=COL_SUBTLE)
        self.status.pack(side="bottom", fill="x")
        self.canvas = tk.Canvas(
            root, width=CANVAS_W, height=CANVAS_H, bg=COL_BG, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.master.app = self

        self.modules: list[Module] = []
        self.cables: list[Cable] = []
        self.drag_src_port: Port | None = None
        self.temp_line: int | None = None

        self.modes = {
            "add": ModeSpec("Add Module", "Click canvas to add a module"),
            "wire": ModeSpec(
                "Wire Mode",
                "Click an OUTPUT, drag, drop on an INPUT to connect. Right-click a cable to delete.",
            ),
            "math": ModeSpec(
                "Define Math",
                "Double-click a module to set inputs, outputs, and Python code",
            ),
        }
        self._build_toolbar()
        self.set_mode("wire")

        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)

        # seed example
        self._add_module(
            200,
            200,
            "Company X",
            inputs=("subsidies", "revenues", "worker_output"),
            outputs=("taxes", "salary"),
            code="salary = 0.6 * worker_output\n"
            "taxes  = 0.2 * max(0, revenues + subsidies - salary)\n",
        )
        self._add_module(
            650,
            200,
            "Worker Y",
            inputs=("salary", "satisfaction", "goods"),
            outputs=("taxes", "productive_work"),
            code="productive_work = (salary/10000*0.5 + satisfaction*0.3 + goods/10000*0.2) * 10000\n"
            "taxes = 0.2 * salary\n",
        )

        self._tick()

    # --- toolbar / modes -----------------------------------------------------

    def _build_toolbar(self):
        for key, ms in self.modes.items():
            b = tk.Button(
                self.toolbar,
                text=ms.name,
                relief="flat",
                padx=10,
                pady=6,
                bg="#24242a",
                fg=COL_TEXT,
                activebackground="#34343a",
                activeforeground="#ffffff",
                command=lambda k=key: self.set_mode(k),
            )
            b.pack(side="left", padx=6, pady=6)
            ms.button = b
            b.bind("<Enter>", lambda e, t=ms.tooltip: self._status(t))
            b.bind("<Leave>", lambda e: self._status(""))

    def set_mode(self, key):
        for k, ms in self.modes.items():
            ms.active = k == key
            if ms.button:
                ms.button.configure(bg="#3a3a44" if ms.active else "#24242a")
        self._status(self.modes[key].tooltip)

    def _status(self, text):
        self.status.configure(text=text)

    # --- module ops ----------------------------------------------------------

    def _add_module(
        self, x, y, title="Module", inputs=("in",), outputs=("out",), code=""
    ):
        m = Module(self.canvas, x, y, title, inputs, outputs, code)
        self.modules.append(m)
        return m

    # --- events --------------------------------------------------------------

    def _on_left_click(self, e):
        if self._active_mode() != "add":
            return
        items = self.canvas.find_overlapping(e.x, e.y, e.x, e.y)
        tags = set(sum((self.canvas.gettags(i) for i in items), ()))
        if "module" in tags or "port" in tags:
            return
        self._add_module(e.x - 105, e.y - 95, title=f"Module {len(self.modules)+1}")

    def _on_double_click(self, e):
        if self._active_mode() != "math":
            return
        for i in self.canvas.find_overlapping(e.x, e.y, e.x, e.y):
            if "module" in self.canvas.gettags(i):
                next(m for m in self.modules if m.id_rect == i).open_editor()
                return

    def _on_motion(self, e):
        if self.temp_line and self.drag_src_port:
            x1, y1 = self.drag_src_port.pos()
            mx = (x1 + e.x) / 2
            self.canvas.coords(self.temp_line, x1, y1, mx, y1, mx, e.y, e.x, e.y)

    def _on_left_release(self, e):
        if not (self.temp_line and self.drag_src_port):
            return
        target = None
        for m in self.modules:
            for p in m.inputs:
                px, py = p.pos()
                if within_circle(e.x, e.y, px, py):
                    target = p
                    break
            if target:
                break
        try:
            self.canvas.delete(self.temp_line)
        except tk.TclError:
            pass
        self.temp_line = None
        if target:
            self.cables.append(Cable(self.canvas, self.drag_src_port, target))
        self.drag_src_port = None

    # --- wiring --------------------------------------------------------------

    def begin_wire_drag(self, src: Port):
        if self._active_mode() != "wire":
            self._status("Switch to Wire Mode to draw cables.")
            return
        self.drag_src_port = src
        x, y = src.pos()
        self.temp_line = self.canvas.create_line(
            x, y, x, y, fill=COL_TEMP, width=2, dash=(5, 3), capstyle="round"
        )

    def _active_mode(self):
        return next((k for k, ms in self.modes.items() if ms.active), "wire")

    # --- simulation ----------------------------------------------------------

    def _tick(self):
        for m in self.modules:
            for p in m.inputs:
                p.value = 0.0

        for c in list(self.cables):
            try:
                c.redraw()
            except tk.TclError:
                continue
            c.dst.value += float(c.src.value)

        for m in self.modules:
            inputs = {p.name: float(p.value) for p in m.inputs}
            results = m.evaluate(inputs)
            out_by_name = {p.name: p for p in m.outputs}
            for name, val in results.items():
                if name in out_by_name:
                    out_by_name[name].value = float(val)
            for p in m.outputs:
                p.value = float(getattr(p, "value", 0.0))

        for m in self.modules:
            for p in (*m.inputs, *m.outputs):
                if p.id_value:
                    self.canvas.itemconfigure(p.id_value, text=f"{p.value:.2f}")

        self.root.after(125, self._tick)


# --- run ---------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
