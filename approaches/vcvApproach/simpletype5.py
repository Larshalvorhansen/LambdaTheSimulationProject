import tkinter as tk
from tkinter import ttk
import math
import random
from dataclasses import dataclass, field

# --- constants / palette (inspired by #fff, #e9eaeb, #1d1d1d, #2fa6ff, #003862) -----

PORT_R = 7
CANVAS_W, CANVAS_H = 1100, 680

COL_BG = "#1d1d1d"  # canvas background
COL_PANEL = "#003862"  # toolbar/status
COL_CARD = "#e9eaeb"  # module card
COL_STROKE = "#ffffff"  # outlines
COL_TEXT = "#ffffff"  # text on dark
COL_TEXT_D = "#1d1d1d"  # text on light cards
COL_ACCENT = "#2fa6ff"  # accent (wires/buttons)

COL_IN = "#2fa6ff"
COL_OUT = "#ffffff"
COL_WIRE = "#2fa6ff"
COL_TEMP = "#e9eaeb"
COL_SUBTLE = "#e9eaeb"

# ROGBIV pool for scope traces
ROGBIV = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#8B00FF"]

# --- utils -------------------------------------------------------------------


def within_circle(x, y, cx, cy, r=PORT_R + 2):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


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
    """Generic compute module — can be subclassed for special rendering like Scope."""

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
                fill=COL_TEXT_D,
                font=("Arial", 12, "bold"),
            )
        else:
            self.canvas.coords(self.id_title, self.x + self.w / 2, self.y + 16)
            self.canvas.itemconfigure(self.id_title, text=self.title)

        # clear old ports
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
                outline=COL_STROKE,
                width=1,
                tags=("port", kind),
            )
            label_x = px + 13 if side == "left" else px - 13
            p.id_label = self.canvas.create_text(
                label_x,
                py,
                text=name,
                fill=COL_TEXT_D,
                font=("Arial", 9),
                anchor=anchor,
            )
            p.id_value = self.canvas.create_text(
                px, py - 15, text="0.0", fill=COL_ACCENT, font=("Arial", 8)
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
        dlg.configure(bg=COL_BG)
        dlg.geometry("640x520")
        dlg.grab_set()

        mklabel = lambda r, c, t: tk.Label(dlg, text=t, fg=COL_TEXT, bg=COL_BG).grid(
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
            dlg, width=70, height=18, bg=COL_BG, fg=COL_TEXT, insertbackground=COL_TEXT
        )
        txt.insert("1.0", self.code.strip() or "# Example:\n# y = a + b\n")
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


class Scope(Module):
    """A module that plots each input over time inside its rectangle."""

    def __init__(self, canvas, x, y, title="Scope", inputs=(), history=200):
        if not inputs:
            # default 4 inputs
            inputs = ("in1", "in2", "in3", "in4")
        self.history_len = history
        self.history = {name: [0.0] * history for name in inputs}
        self.colors = {}  # input name -> color from ROGBIV (stable)
        super().__init__(canvas, x, y, title=title, inputs=inputs, outputs=(), code="")
        self.w, self.h = 300, 200  # scope a bit wider
        self._draw()

    def _make_ports(self, names, side="left"):
        # same as Module but assign colors for each input
        ports = super()._make_ports(names, side)
        for name in names:
            if name not in self.colors:
                self.colors[name] = random.choice(ROGBIV)
        return ports

    def evaluate(self, inputs_dict: dict[str, float]) -> dict[str, float]:
        # update history for each input
        for name in self.history.keys():
            v = float(inputs_dict.get(name, 0.0))
            buf = self.history[name]
            buf.append(v)
            if len(buf) > self.history_len:
                del buf[0]
        # no outputs
        return {}

    def _draw(self):
        super()._draw()
        # draw grid/axes (clear previous scope drawings)
        # remove existing plot lines by deleting with a tag
        self.canvas.delete(f"scope_{id(self)}")

        # draw scope frame area
        pad = 28
        x0, y0 = self.x + 8, self.y + pad
        x1, y1 = self.x + self.w - 8, self.y + self.h - 10
        self.canvas.create_rectangle(
            x0, y0, x1, y1, outline=COL_STROKE, width=1, tags=(f"scope_{id(self)}",)
        )
        # grid lines
        for i in range(1, 5):
            yy = y0 + (y1 - y0) * i / 5
            self.canvas.create_line(
                x0,
                yy,
                x1,
                yy,
                fill="#cfd3d7",
                width=1,
                dash=(3, 3),
                tags=(f"scope_{id(self)}",),
            )

    def render_plot(self):
        # re-render plot lines
        self.canvas.delete(f"scope_plot_{id(self)}")
        pad = 28
        x0, y0 = self.x + 8, self.y + pad
        x1, y1 = self.x + self.w - 8, self.y + self.h - 10
        w = max(1, x1 - x0)
        h = max(1, y1 - y0)

        # map value to y: assume interesting range [-1, +1] auto-clipped
        def map_y(v):
            v = max(-1.0, min(1.0, v))
            # 1 -> top, -1 -> bottom
            return y0 + (1 - (v + 1) / 2) * h

        xs = [x0 + i * (w / (self.history_len - 1)) for i in range(self.history_len)]

        for name, buf in self.history.items():
            if len(buf) < 2:
                continue
            pts = []
            for i, v in enumerate(buf[-self.history_len :]):
                pts.extend([xs[i], map_y(v)])
            self.canvas.create_line(
                *pts,
                fill=self.colors.get(name, COL_ACCENT),
                width=2,
                smooth=True,
                tags=(f"scope_plot_{id(self)}",),
            )
        # legend
        lx, ly = x0 + 6, y0 - 10
        for i, (name, col) in enumerate(self.colors.items()):
            self.canvas.create_text(
                lx + i * 60,
                ly,
                text=name,
                fill=col,
                font=("Arial", 8, "bold"),
                anchor="w",
                tags=(f"scope_plot_{id(self)}",),
            )


# --- platform / app ----------------------------------------------------------


@dataclass
class ModeSpec:
    name: str
    tooltip: str
    active: bool = False
    button: ttk.Button | None = field(default=None, compare=False)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Economic Patch Platform — mini")

        # ttk styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Tool.TButton",
            background=COL_ACCENT,
            foreground=COL_TEXT,
            bordercolor=COL_ACCENT,
            focusthickness=0,
            padding=6,
            relief="flat",
        )
        self.style.map(
            "Tool.TButton",
            background=[("active", COL_TEMP), ("pressed", COL_TEMP)],
            foreground=[("active", COL_BG), ("pressed", COL_BG)],
        )
        self.style.configure(
            "ToolActive.TButton",
            background=COL_TEMP,
            foreground=COL_BG,
            bordercolor=COL_TEMP,
            padding=6,
            relief="flat",
        )

        # top bar + status + canvas
        self.toolbar = tk.Frame(root, bg=COL_PANEL)
        self.toolbar.pack(side="top", fill="x")

        self.status = tk.Label(
            root, text="Ready", anchor="w", bg=COL_PANEL, fg=COL_SUBTLE
        )
        self.status.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(
            root, width=CANVAS_W, height=CANVAS_H, bg=COL_BG, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.master.app = self

        # sim state
        self.running = False
        self.paused = False
        self.tick_interval = 250  # ms
        self.zoom = 1.0

        # data structures
        self.modules: list[Module] = []
        self.cables: list[Cable] = []
        self.drag_src_port: Port | None = None
        self.temp_line: int | None = None

        # move mode drag state
        self.move_active = False
        self.move_target: Module | None = None
        self.move_dx = 0
        self.move_dy = 0

        # modes
        self.modes = {
            "add": ModeSpec("Add (Q)", "Click canvas to add a module"),
            "wire": ModeSpec(
                "Wire (W)",
                "Click OUTPUT → drag → INPUT. Right-click a cable to delete.",
            ),
            "math": ModeSpec("Math (E)", "Double-click a module to edit its code/IO."),
            "delete": ModeSpec("Delete (D)", "Click a module to delete it"),
            "move": ModeSpec("Move (M)", "Drag a module to reposition it"),
        }

        self._build_toolbar()
        self._bind_hotkeys()
        self.set_mode("wire")

        # canvas events
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)
        self.canvas.bind("<Motion>", self._on_motion)

        # seed example modules
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
        # scope example
        self._add_scope(420, 420, inputs=("taxes_total", "work", "noise"))

        # (optional) start paused; use controls to run
        self._status("Use Start/Pause/Stop/Step • Q/W/E/D/M hotkeys for modes")

    # --- toolbar / controls --------------------------------------------------

    def _build_toolbar(self):
        # simulation controls (left)
        ctrl = tk.Frame(self.toolbar, bg=COL_PANEL)
        ctrl.pack(side="left", padx=6, pady=6)

        ttk.Button(
            ctrl, text="Start", command=self._start_sim, style="Tool.TButton"
        ).pack(side="left", padx=3)
        ttk.Button(
            ctrl, text="Pause", command=self._pause_sim, style="Tool.TButton"
        ).pack(side="left", padx=3)
        ttk.Button(
            ctrl, text="Stop", command=self._stop_sim, style="Tool.TButton"
        ).pack(side="left", padx=3)
        ttk.Button(
            ctrl, text="Step", command=self._step_sim, style="Tool.TButton"
        ).pack(side="left", padx=3)

        tk.Label(ctrl, text=" Speed", bg=COL_PANEL, fg=COL_SUBTLE).pack(
            side="left", padx=(8, 3)
        )
        self.speed = tk.Scale(
            ctrl,
            from_=1,
            to=100,
            orient="horizontal",
            bg=COL_PANEL,
            fg=COL_TEXT,
            troughcolor=COL_BG,
            highlightthickness=0,
            command=self._set_speed,
            length=140,
        )
        self.speed.set(50)
        self.speed.pack(side="left")

        # modes (right of controls)
        modes_frame = tk.Frame(self.toolbar, bg=COL_PANEL)
        modes_frame.pack(side="left", padx=10)

        for key, ms in self.modes.items():
            b = ttk.Button(
                modes_frame,
                text=ms.name,
                style="Tool.TButton",
                command=lambda k=key: self.set_mode(k),
            )
            b.pack(side="left", padx=5)
            ms.button = b
            b.bind("<Enter>", lambda e, t=ms.tooltip: self._status(t))
            b.bind("<Leave>", lambda e: self._status(""))

    def set_mode(self, key):
        for k, ms in self.modes.items():
            ms.active = k == key
            if ms.button:
                ms.button.configure(
                    style="ToolActive.TButton" if ms.active else "Tool.TButton"
                )
        self._status(self.modes[key].tooltip)

    def _status(self, text):
        self.status.configure(text=text)

    # --- hotkeys -------------------------------------------------------------

    def _bind_hotkeys(self):
        for seq, mode in (
            ("<q>", "add"),
            ("<w>", "wire"),
            ("<e>", "math"),
            ("<d>", "delete"),
            ("<m>", "move"),
            ("<Q>", "add"),
            ("<W>", "wire"),
            ("<E>", "math"),
            ("<D>", "delete"),
            ("<M>", "move"),
        ):
            self.root.bind_all(seq, lambda e, m=mode: self.set_mode(m))

        # zoom (optional; comment if not needed)
        self.root.bind_all("<Command-plus>", self._zoom_in)
        self.root.bind_all("<Command-minus>", self._zoom_out)
        self.root.bind_all("<Control-plus>", self._zoom_in)
        self.root.bind_all("<Control-minus>", self._zoom_out)

    # --- simulation control --------------------------------------------------

    def _start_sim(self):
        self.running = True
        self.paused = False
        self._tick()

    def _pause_sim(self):
        if self.running:
            self.paused = not self.paused
            self._status("Paused" if self.paused else "Running")

    def _stop_sim(self):
        self.running = False
        self.paused = False
        # reset values
        for m in self.modules:
            for p in (*m.inputs, *m.outputs):
                p.value = 0.0
                if p.id_value:
                    self.canvas.itemconfigure(p.id_value, text="0.00")
        # clear scope histories
        for m in self.modules:
            if isinstance(m, Scope):
                for k in m.history:
                    m.history[k] = [0.0] * m.history_len
                m._draw()
                m.render_plot()
        self._status("Stopped")

    def _step_sim(self):
        if not self.running:
            self.running = True
            self.paused = True
        self._do_tick()  # single step

    def _set_speed(self, val):
        v = int(val)
        # map 1..100 -> 1000..20 ms (fast when higher)
        self.tick_interval = int(1000 - (v - 1) * (980 / 99))

    # --- add/delete/move modules --------------------------------------------

    def _add_module(
        self, x, y, title="Module", inputs=("in",), outputs=("out",), code=""
    ):
        m = Module(self.canvas, x, y, title, inputs, outputs, code)
        self.modules.append(m)
        return m

    def _add_scope(self, x, y, inputs=("in1", "in2", "in3", "in4")):
        s = Scope(self.canvas, x, y, inputs=inputs)
        self.modules.append(s)
        return s

    def _delete_module(self, module):
        for c in [
            c for c in self.cables if c.src.module is module or c.dst.module is module
        ]:
            c._remove()
        for p in module.inputs + module.outputs:
            for item in (p.id_circle, p.id_label, p.id_value):
                if item:
                    self.canvas.delete(item)
        if module.id_rect:
            self.canvas.delete(module.id_rect)
        if module.id_title:
            self.canvas.delete(module.id_title)
        if module in self.modules:
            self.modules.remove(module)

    # --- events --------------------------------------------------------------

    def _on_left_click(self, e):
        mode = self._active_mode()

        if mode == "add":
            items = self.canvas.find_overlapping(e.x, e.y, e.x, e.y)
            tags = set(sum((self.canvas.gettags(i) for i in items), ()))
            if "module" in tags or "port" in tags:
                return
            # Holding Shift while in add mode creates a Scope instead
            if e.state & 0x0001:  # Shift
                self._add_scope(e.x - 150, e.y - 100, inputs=("a", "b", "c", "d", "e"))
            else:
                self._add_module(
                    e.x - 105, e.y - 95, title=f"Module {len(self.modules)+1}"
                )

        elif mode == "delete":
            for i in self.canvas.find_overlapping(e.x, e.y, e.x, e.y):
                if "module" in self.canvas.gettags(i):
                    m = next(m for m in self.modules if m.id_rect == i)
                    self._delete_module(m)
                    return

        elif mode == "move":
            # start drag on module rect
            for i in self.canvas.find_overlapping(e.x, e.y, e.x, e.y):
                if "module" in self.canvas.gettags(i):
                    m = next(m for m in self.modules if m.id_rect == i)
                    self.move_active = True
                    self.move_target = m
                    self.move_dx = e.x - m.x
                    self.move_dy = e.y - m.y
                    return

    def _on_drag(self, e):
        if self._active_mode() == "move" and self.move_active and self.move_target:
            m = self.move_target
            m.x = e.x - self.move_dx
            m.y = e.y - self.move_dy
            m._draw()
            # redraw cables attached
            for c in self.cables:
                if c.src.module is m or c.dst.module is m:
                    c.redraw()
            # refresh scope plot frame if needed
            if isinstance(m, Scope):
                m._draw()
                m.render_plot()

    def _on_left_release(self, e):
        if self.temp_line and self.drag_src_port:
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

        if self._active_mode() == "move":
            self.move_active = False
            self.move_target = None

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
        if self.running and not self.paused:
            self._do_tick()
        if self.running:
            self.root.after(self.tick_interval, self._tick)

    def _do_tick(self):
        # zero inputs
        for m in self.modules:
            for p in m.inputs:
                p.value = 0.0

        # propagate through cables (sum if multiple)
        for c in list(self.cables):
            try:
                c.redraw()
            except tk.TclError:
                continue
            c.dst.value += float(c.src.value)

        # evaluate modules
        for m in self.modules:
            inputs = {p.name: float(p.value) for p in m.inputs}
            # little example: feed some noise if input name 'noise' exists
            if "noise" in inputs:
                inputs["noise"] = (random.random() - 0.5) * 2.0  # -1..1
            results = m.evaluate(inputs)
            out_by_name = {p.name: p for p in m.outputs}
            for name, val in results.items():
                if name in out_by_name:
                    out_by_name[name].value = float(val)
            for p in m.outputs:
                p.value = float(getattr(p, "value", 0.0))

        # update value labels
        for m in self.modules:
            for p in (*m.inputs, *m.outputs):
                if p.id_value:
                    self.canvas.itemconfigure(p.id_value, text=f"{p.value:.2f}")

        # render scopes
        for m in self.modules:
            if isinstance(m, Scope):
                m._draw()
                m.render_plot()

    # --- zoom (optional) -----------------------------------------------------

    def _zoom_in(self, event=None):
        self._apply_zoom(1.1)

    def _zoom_out(self, event=None):
        self._apply_zoom(0.9)

    def _apply_zoom(self, factor):
        self.zoom *= factor
        self.canvas.scale("all", 0, 0, factor, factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


# --- run ---------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
