import tkinter as tk
from tkinter import simpledialog, messagebox
import math
from dataclasses import dataclass, field

PORT_R = 7
CANVAS_W, CANVAS_H = 1100, 680

# --------------------------
# Utilities
# --------------------------


def within_circle(x, y, cx, cy, r=PORT_R + 2):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r**2


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# --------------------------
# Dataflow primitives
# --------------------------


class Port:
    def __init__(self, module, name, kind, relx, rely):
        self.module = module
        self.name = name
        self.kind = kind  # "in" or "out"
        self.relx = relx
        self.rely = rely
        self.value = 0.0
        self.id_circle = None
        self.id_label = None
        self.id_value = None

    def pos(self):
        return self.module.x + self.relx, self.module.y + self.rely


class Cable:
    def __init__(self, canvas, src_port: Port, dst_port: Port):
        self.canvas = canvas
        self.src = src_port
        self.dst = dst_port
        self.id_line = canvas.create_line(
            *self._points(),
            smooth=True,
            splinesteps=24,
            width=3,
            fill="#39d5ff",
            capstyle="round",
        )
        canvas.tag_bind(self.id_line, "<Button-3>", self._remove)

    def _points(self):
        x1, y1 = self.src.pos()
        x2, y2 = self.dst.pos()
        midx = (x1 + x2) / 2
        return (x1, y1, midx, y1, midx, y2, x2, y2)

    def redraw(self):
        self.canvas.coords(self.id_line, *self._points())

    def _remove(self, _evt=None):
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
        self.canvas = canvas
        self.x, self.y = x, y
        self.w, self.h = 210, 190
        self.title = title
        self.inputs_def = list(inputs)
        self.outputs_def = list(outputs)
        # default code: passthrough/sum
        if not code:
            if self.outputs_def:
                code = (
                    f"{self.outputs_def[0]} = "
                    f"{' + '.join(self.inputs_def) if self.inputs_def else '0.0'}"
                )
            else:
                code = "# define outputs here"
        self.code = code

        self.id_rect = None
        self.id_title = None
        self.inputs = []
        self.outputs = []
        self._draw()

    # ---------- drawing ----------
    def _draw(self):
        # base rect
        if self.id_rect is None:
            self.id_rect = self.canvas.create_rectangle(
                self.x,
                self.y,
                self.x + self.w,
                self.y + self.h,
                fill="#1f1f24",
                outline="#7a7a88",
                width=2,
                tags=("module",),
            )
        else:
            self.canvas.coords(
                self.id_rect, self.x, self.y, self.x + self.w, self.y + self.h
            )
        # title
        if self.id_title is None:
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

        # recreate ports
        self._clear_ports()
        self.inputs = self._make_ports(self.inputs_def, side="left")
        self.outputs = self._make_ports(self.outputs_def, side="right")

    def _clear_ports(self):
        for p in getattr(self, "inputs", []):
            for item in (p.id_circle, p.id_label, p.id_value):
                if item:
                    self.canvas.delete(item)
        for p in getattr(self, "outputs", []):
            for item in (p.id_circle, p.id_label, p.id_value):
                if item:
                    self.canvas.delete(item)

    def _make_ports(self, names, side="left"):
        ports = []
        n = max(1, len(names))
        top = 44
        gap = (self.h - top - 16) / n
        for i, name in enumerate(names):
            y = top + gap * i + 12
            x = 18 if side == "left" else self.w - 18
            p = Port(self, name, "in" if side == "left" else "out", x, y)
            px, py = p.pos()
            color = "#ff7676" if p.kind == "in" else "#44d17a"
            p.id_circle = self.canvas.create_oval(
                px - PORT_R,
                py - PORT_R,
                px + PORT_R,
                py + PORT_R,
                fill=color,
                outline="#000",
                width=1,
                tags=("port", p.kind),
            )
            # labels
            if side == "left":
                p.id_label = self.canvas.create_text(
                    px + 13,
                    py,
                    text=name,
                    fill="#e6e6f0",
                    font=("Arial", 9),
                    anchor="w",
                )
            else:
                p.id_label = self.canvas.create_text(
                    px - 13,
                    py,
                    text=name,
                    fill="#e6e6f0",
                    font=("Arial", 9),
                    anchor="e",
                )
            p.id_value = self.canvas.create_text(
                px, py - 15, text="0.0", fill="#b5e3ff", font=("Arial", 8)
            )
            # output interactions (start wire)
            if p.kind == "out":
                self.canvas.tag_bind(
                    p.id_circle, "<Button-1>", lambda e, port=p: self._start_wire(port)
                )
        return ports

    def _start_wire(self, port: Port):
        self.canvas.master.app.begin_wire_drag(port)

    # ---------- math ----------
    def evaluate(self, inputs_dict):
        """
        inputs_dict: {input_name: float}
        code has access to variables named after inputs; write outputs by assigning to their names.
        """
        env = {}
        # seed inputs
        for k, v in inputs_dict.items():
            # make safe-ish identifiers (already assumed to be simple names)
            env[k] = float(v)
        # allow math functions
        globals_dict = {"__builtins__": {}, "math": math}
        try:
            exec(self.code, globals_dict, env)
        except Exception as e:
            # on error, zero outputs and annotate title temporarily
            # (you could surface errors better in a console)
            # print("Exec error in module", self.title, e)
            pass
        results = {}
        for out_name in self.outputs_def:
            results[out_name] = float(env.get(out_name, 0.0))
        return results

    # ---------- edit ----------
    def open_editor(self):
        dlg = tk.Toplevel(self.canvas.master)
        dlg.title(f"Define Math • {self.title}")
        dlg.configure(bg="#26262c")
        dlg.geometry("640x520")
        dlg.grab_set()

        # Title
        tk.Label(dlg, text="Title", fg="white", bg="#26262c").grid(
            row=0, column=0, sticky="w", padx=10, pady=(12, 4)
        )
        e_title = tk.Entry(dlg, width=30)
        e_title.insert(0, self.title)
        e_title.grid(row=0, column=1, padx=10, pady=(12, 4), sticky="w")

        # Inputs
        tk.Label(dlg, text="Inputs (comma-separated)", fg="white", bg="#26262c").grid(
            row=1, column=0, sticky="w", padx=10, pady=4
        )
        e_in = tk.Entry(dlg, width=50)
        e_in.insert(0, ", ".join(self.inputs_def))
        e_in.grid(row=1, column=1, padx=10, pady=4, sticky="we")

        # Outputs
        tk.Label(dlg, text="Outputs (comma-separated)", fg="white", bg="#26262c").grid(
            row=2, column=0, sticky="w", padx=10, pady=4
        )
        e_out = tk.Entry(dlg, width=50)
        e_out.insert(0, ", ".join(self.outputs_def))
        e_out.grid(row=2, column=1, padx=10, pady=4, sticky="we")

        # Code
        tk.Label(
            dlg, text="Python code (assign outputs)", fg="white", bg="#26262c"
        ).grid(row=3, column=0, sticky="nw", padx=10, pady=4)
        txt = tk.Text(
            dlg,
            width=70,
            height=18,
            bg="#1e1e22",
            fg="#eaeaf0",
            insertbackground="white",
        )
        if not self.code.strip():
            example = (
                "# Example:\n"
                "# salary = 0.6 * worker_output\n"
                "# taxes  = 0.2 * max(0, revenues + subsidies - salary)\n"
            )
            txt.insert("1.0", example)
        else:
            txt.insert("1.0", self.code)
        txt.grid(row=3, column=1, padx=10, pady=4, sticky="nsew")

        dlg.grid_columnconfigure(1, weight=1)
        dlg.grid_rowconfigure(3, weight=1)

        def save():
            new_title = e_title.get().strip() or "Module"
            ins = [s.strip() for s in e_in.get().split(",") if s.strip()]
            outs = [s.strip() for s in e_out.get().split(",") if s.strip()]
            new_code = txt.get("1.0", "end-1c")
            # remove cables connected to ports that might disappear
            self._remove_cables_touching_ports()
            self.title = new_title
            self.inputs_def = ins or ["in"]
            self.outputs_def = outs or ["out"]
            self.code = new_code or "# define outputs here"
            self._draw()
            dlg.destroy()

        tk.Button(dlg, text="Save", command=save).grid(
            row=4, column=0, columnspan=2, pady=10
        )

    def _remove_cables_touching_ports(self):
        app = self.canvas.master.app
        to_remove = []
        for c in app.cables:
            if c.src.module is self or c.dst.module is self:
                to_remove.append(c)
        for c in to_remove:
            c._remove()


# --------------------------
# App / Platform
# --------------------------


@dataclass
class ModeSpec:
    name: str
    tooltip: str
    active: bool = False
    button: tk.Button = field(default=None, compare=False)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Economic Patch Platform — mini")
        # top toolbar
        self.toolbar = tk.Frame(root, bg="#17171b")
        self.toolbar.pack(side="top", fill="x")
        # status / tooltip
        self.status = tk.Label(
            root, text="Ready", anchor="w", bg="#0f0f14", fg="#b8bec9"
        )
        self.status.pack(side="bottom", fill="x")

        # canvas
        self.canvas = tk.Canvas(
            root, width=CANVAS_W, height=CANVAS_H, bg="#0f0f14", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.master.app = self

        # state
        self.modules = []
        self.cables = []
        self.drag_src_port = None
        self.temp_line = None

        # modes
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
        self.set_mode("wire")  # default

        # bindings (global)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)

        # seed example modules
        self._add_module(
            200,
            200,
            "Company X",
            inputs=("subsidies", "revenues", "worker_output"),
            outputs=("taxes", "salary"),
            code=(
                "salary = 0.6 * worker_output\n"
                "taxes  = 0.2 * max(0, revenues + subsidies - salary)\n"
            ),
        )
        self._add_module(
            650,
            200,
            "Worker Y",
            inputs=("salary", "satisfaction", "goods"),
            outputs=("taxes", "productive_work"),
            code=(
                "productive_work = (salary/10000*0.5 + satisfaction*0.3 + goods/10000*0.2) * 10000\n"
                "taxes = 0.2 * salary\n"
            ),
        )

        # simulation loop
        self._tick()

    # ---------- toolbar ----------
    def _build_toolbar(self):
        def make_btn(key):
            ms = self.modes[key]
            b = tk.Button(
                self.toolbar,
                text=ms.name,
                relief="flat",
                padx=10,
                pady=6,
                bg="#24242a",
                fg="#e6e6f0",
                activebackground="#34343a",
                activeforeground="#ffffff",
                command=lambda k=key: self.set_mode(k),
            )
            b.pack(side="left", padx=6, pady=6)
            ms.button = b
            # tooltip via status bar
            b.bind("<Enter>", lambda e, t=ms.tooltip: self._status(t))
            b.bind("<Leave>", lambda e: self._status(""))

        for key in self.modes:
            make_btn(key)

    def set_mode(self, key):
        for k, ms in self.modes.items():
            ms.active = k == key
            if ms.button:
                ms.button.configure(bg="#3a3a44" if ms.active else "#24242a")
        self._status(self.modes[key].tooltip)

    def _status(self, text):
        self.status.configure(text=text)

    # ---------- module ops ----------
    def _add_module(
        self, x, y, title="Module", inputs=("in",), outputs=("out",), code=""
    ):
        m = Module(self.canvas, x, y, title, inputs, outputs, code)
        self.modules.append(m)
        return m

    # ---------- event handlers ----------
    def _on_left_click(self, evt):
        mode = self._active_mode()
        if mode == "add":
            # only add if clicking empty space
            items = self.canvas.find_overlapping(evt.x, evt.y, evt.x, evt.y)
            tags = set(sum((self.canvas.gettags(i) for i in items), ()))
            if "module" in tags or "port" in tags:
                return
            self._add_module(
                evt.x - 105, evt.y - 95, title=f"Module {len(self.modules)+1}"
            )
            return
        elif mode == "wire":
            # handled by port bindings (start from outputs)
            return
        # math mode: clicks do nothing, double-click opens editor

    def _on_double_click(self, evt):
        if self._active_mode() != "math":
            return
        # if double-click hits a module, open editor
        items = self.canvas.find_overlapping(evt.x, evt.y, evt.x, evt.y)
        for i in items:
            if "module" in self.canvas.gettags(i):
                # find module by rect id
                for m in self.modules:
                    if m.id_rect == i:
                        m.open_editor()
                        return

    def _on_motion(self, evt):
        if self.temp_line and self.drag_src_port:
            x1, y1 = self.drag_src_port.pos()
            midx = (x1 + evt.x) / 2
            self.canvas.coords(
                self.temp_line, x1, y1, midx, y1, midx, evt.y, evt.x, evt.y
            )

    def _on_left_release(self, evt):
        if not self.temp_line or not self.drag_src_port:
            return
        # find input under release point
        target = None
        for m in self.modules:
            for p in m.inputs:
                px, py = p.pos()
                if within_circle(evt.x, evt.y, px, py):
                    target = p
                    break
            if target:
                break
        # remove temp
        try:
            self.canvas.delete(self.temp_line)
        except tk.TclError:
            pass
        self.temp_line = None

        if target:
            # allow multiple cables to same input (sum)
            cable = Cable(self.canvas, self.drag_src_port, target)
            self.cables.append(cable)
        self.drag_src_port = None

    # ---------- wire drag entry ----------
    def begin_wire_drag(self, src_port: Port):
        if self._active_mode() != "wire":
            self._status("Switch to Wire Mode to draw cables.")
            return
        self.drag_src_port = src_port
        x, y = src_port.pos()
        self.temp_line = self.canvas.create_line(
            x, y, x, y, fill="#f5d90a", width=2, dash=(5, 3), capstyle="round"
        )

    # ---------- mode helper ----------
    def _active_mode(self):
        for k, ms in self.modes.items():
            if ms.active:
                return k
        return "wire"

    # ---------- simulation / redraw ----------
    def _tick(self):
        # 1) reset all input values to 0
        for m in self.modules:
            for p in m.inputs:
                p.value = 0.0

        # 2) propagate along cables (sum at inputs)
        for c in list(self.cables):
            try:
                c.redraw()
            except tk.TclError:
                continue
            c.dst.value += float(c.src.value)

        # 3) evaluate each module
        # build input dicts by name
        for m in self.modules:
            inputs_by_name = {}
            for p in m.inputs:
                inputs_by_name[p.name] = float(p.value)
            results = m.evaluate(inputs_by_name)
            # assign out values to output ports in order (by name match)
            name_to_port = {p.name: p for p in m.outputs}
            for out_name, out_val in results.items():
                if out_name in name_to_port:
                    name_to_port[out_name].value = float(out_val)
            # any outputs not set get 0
            for p in m.outputs:
                p.value = float(getattr(p, "value", 0.0))

        # 4) update port value labels
        for m in self.modules:
            for p in m.inputs + m.outputs:
                if p.id_value:
                    self.canvas.itemconfigure(p.id_value, text=f"{p.value:.2f}")

        # schedule next tick
        self.root.after(125, self._tick)


# --------------------------
# Run
# --------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
