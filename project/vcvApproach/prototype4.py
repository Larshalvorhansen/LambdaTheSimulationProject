import tkinter as tk
from tkinter import simpledialog, messagebox

# --------------------------
# Core primitives
# --------------------------

PORT_RADIUS = 7


def within(x, y, cx, cy, r=PORT_RADIUS + 2):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r**2


class Port:
    def __init__(self, module, name, kind, x, y):
        self.module = module
        self.name = name
        self.kind = kind  # "in" or "out"
        self.rx, self.ry = x, y  # relative to module top-left
        self.id_circle = None

    def pos(self):
        return self.module.x + self.rx, self.module.y + self.ry


class Cable:
    def __init__(self, canvas, src_port: Port, dst_port: Port):
        self.canvas = canvas
        self.src = src_port
        self.dst = dst_port
        self.id_line = canvas.create_line(
            *self.points(),
            smooth=True,
            splinesteps=24,
            width=3,
            fill="#39d5ff",
            capstyle="round",
        )
        # right-click removal
        canvas.tag_bind(self.id_line, "<Button-3>", self._remove)

    def _remove(self, _evt=None):
        self.canvas.delete(self.id_line)
        app = self.canvas.master.app
        if self in app.cables:
            app.cables.remove(self)

    def points(self):
        x1, y1 = self.src.pos()
        x2, y2 = self.dst.pos()
        midx = (x1 + x2) / 2
        # horizontal bezier-ish with two control points
        return (x1, y1, midx, y1, midx, y2, x2, y2)

    def redraw(self):
        self.canvas.coords(self.id_line, *self.points())


class Module:
    def __init__(self, canvas, x, y, title="Module", inputs=("in",), outputs=("out",)):
        self.canvas = canvas
        self.x, self.y = x, y
        self.w, self.h = 180, 160
        self.title = title
        self.inputs_def = list(inputs)
        self.outputs_def = list(outputs)
        self.id_rect = None
        self.id_title = None
        self.inputs = []
        self.outputs = []
        self.draw()

    def draw(self):
        # base
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
            # double-click to edit I/O
            self.canvas.tag_bind(self.id_rect, "<Double-Button-1>", self.edit_io)
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

        # (re)build ports from defs
        self._clear_ports()
        self.inputs = self._make_ports(self.inputs_def, side="left")
        self.outputs = self._make_ports(self.outputs_def, side="right")

    def _clear_ports(self):
        # remove visuals for previous ports
        for p in getattr(self, "inputs", []):
            if p.id_circle:
                self.canvas.delete(p.id_circle)
        for p in getattr(self, "outputs", []):
            if p.id_circle:
                self.canvas.delete(p.id_circle)

    def _make_ports(self, names, side="left"):
        ports = []
        n = max(1, len(names))
        top = 46
        gap = (self.h - top - 16) / n
        for i, name in enumerate(names):
            y = top + gap * i + 10
            x = 16 if side == "left" else self.w - 16
            p = Port(self, name, "in" if side == "left" else "out", x, y)
            px, py = p.pos()
            color = "#ff6464" if p.kind == "in" else "#44d17a"
            p.id_circle = self.canvas.create_oval(
                px - PORT_RADIUS,
                py - PORT_RADIUS,
                px + PORT_RADIUS,
                py + PORT_RADIUS,
                fill=color,
                outline="#000000",
                width=1,
                tags=("port", p.kind),
            )
            # label
            align = "w" if side == "left" else "e"
            lx = px + 12 if side == "left" else px - 12
            self.canvas.create_text(
                lx,
                py,
                text=name,
                fill="#e6e6f0",
                font=("Arial", 9),
                anchor=align,
                tags=("portlabel",),
            )
            # start connection only from outputs
            if p.kind == "out":
                self.canvas.tag_bind(
                    p.id_circle, "<Button-1>", lambda e, port=p: self._start_drag(port)
                )
            ports.append(p)
        return ports

    def _start_drag(self, port: Port):
        app = self.canvas.master.app
        app.begin_temporary_cable(port)

    def edit_io(self, _evt=None):
        """Double-click module to set title, inputs, outputs."""
        root = self.canvas.master
        dlg = tk.Toplevel(root)
        dlg.title("Edit module")
        dlg.configure(bg="#26262c")
        dlg.grab_set()
        # Title
        tk.Label(dlg, text="Title", fg="white", bg="#26262c").grid(
            row=0, column=0, sticky="w", padx=8, pady=(10, 4)
        )
        e_title = tk.Entry(dlg, width=30)
        e_title.insert(0, self.title)
        e_title.grid(row=0, column=1, padx=8, pady=(10, 4))
        # Inputs
        tk.Label(dlg, text="Inputs (comma-separated)", fg="white", bg="#26262c").grid(
            row=1, column=0, sticky="w", padx=8, pady=4
        )
        e_in = tk.Entry(dlg, width=30)
        e_in.insert(0, ", ".join(self.inputs_def))
        e_in.grid(row=1, column=1, padx=8, pady=4)
        # Outputs
        tk.Label(dlg, text="Outputs (comma-separated)", fg="white", bg="#26262c").grid(
            row=2, column=0, sticky="w", padx=8, pady=4
        )
        e_out = tk.Entry(dlg, width=30)
        e_out.insert(0, ", ".join(self.outputs_def))
        e_out.grid(row=2, column=1, padx=8, pady=4)

        def save_and_close():
            new_title = e_title.get().strip() or "Module"
            ins = [s.strip() for s in e_in.get().split(",") if s.strip()]
            outs = [s.strip() for s in e_out.get().split(",") if s.strip()]
            # Remove any cables linked to ports that will disappear
            self._remove_cables_touching_self()
            self.title = new_title
            self.inputs_def = ins or ["in"]
            self.outputs_def = outs or ["out"]
            self.draw()
            dlg.destroy()

        tk.Button(dlg, text="Save", command=save_and_close).grid(
            row=3, column=0, columnspan=2, pady=10
        )

    def _remove_cables_touching_self(self):
        app = self.canvas.master.app
        to_remove = []
        for c in app.cables:
            if c.src.module is self or c.dst.module is self:
                to_remove.append(c)
        for c in to_remove:
            c._remove()


# --------------------------
# App
# --------------------------


class App:
    def __init__(self, root):
        self.root = root
        root.title("Mini Rack Patcher")
        self.canvas = tk.Canvas(
            root, width=1000, height=640, bg="#0f0f14", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.master.app = self

        # state
        self.modules = []
        self.cables = []

        # temporary cable drag
        self.drag_src_port = None
        self.temp_line = None

        # instructions
        self._draw_hud()

        # interactions
        self.canvas.bind(
            "<Button-1>", self._maybe_add_module
        )  # click empty = add module
        self.canvas.bind("<Motion>", self._drag_motion)  # update temp wire if exists
        self.canvas.bind("<ButtonRelease-1>", self._finish_drag)

        # seed a couple of modules
        self._add_module(
            160,
            160,
            "Company X",
            inputs=("Subsidies", "Revenues", "Worker out"),
            outputs=("Gov taxes", "Salary"),
        )
        self._add_module(
            560,
            160,
            "Worker Y",
            inputs=("Salary", "Satisfaction", "Goods"),
            outputs=("Gov taxes", "Productive work"),
        )

        # redraw loop (for cable curves when modules move later; cheap here)
        self._tick()

    # ----------------- HUD -----------------
    def _draw_hud(self):
        msg = (
            "click empty canvas: add module • double-click module: set title/IO • "
            "click output → drag → drop on input: connect • right-click cable: delete"
        )
        self.canvas.create_text(
            12, 12, text=msg, fill="#9aa0aa", font=("Arial", 10), anchor="nw"
        )

    # --------------- Modules ---------------
    def _add_module(self, x, y, title="Module", inputs=("in",), outputs=("out",)):
        m = Module(self.canvas, x, y, title, inputs, outputs)
        self.modules.append(m)
        return m

    def _maybe_add_module(self, evt):
        # if click hits a port or module, let their handlers run (Tk will already have bound ports/modules)
        # Here, we only add if the click is on empty space.
        items = self.canvas.find_overlapping(evt.x, evt.y, evt.x, evt.y)
        tags = set(sum((self.canvas.gettags(i) for i in items), ()))
        if "port" in tags or "module" in tags:
            return
        self._add_module(evt.x - 90, evt.y - 80, title=f"Module {len(self.modules)+1}")

    # ------------- Cable Dragging ----------
    def begin_temporary_cable(self, src_port: Port):
        self.drag_src_port = src_port
        x, y = src_port.pos()
        self.temp_line = self.canvas.create_line(
            x, y, x, y, fill="#f5d90a", width=2, dash=(5, 3), capstyle="round"
        )

    def _drag_motion(self, evt):
        if not self.temp_line or not self.drag_src_port:
            return
        x1, y1 = self.drag_src_port.pos()
        midx = (x1 + evt.x) / 2
        self.canvas.coords(self.temp_line, x1, y1, midx, y1, midx, evt.y, evt.x, evt.y)

    def _finish_drag(self, evt):
        if not self.temp_line or not self.drag_src_port:
            return
        # find if released over an input port
        target_port = None
        for m in self.modules:
            for p in m.inputs:
                px, py = p.pos()
                if within(evt.x, evt.y, px, py):
                    target_port = p
                    break
            if target_port:
                break

        # remove temp line
        self.canvas.delete(self.temp_line)
        self.temp_line = None

        if target_port:
            # enforce single cable per input (replace existing)
            existing = [c for c in self.cables if c.dst is target_port]
            for c in existing:
                c._remove()

            cable = Cable(self.canvas, self.drag_src_port, target_port)
            self.cables.append(cable)

        self.drag_src_port = None

    # ------------- Redraw tick -------------
    def _tick(self):
        # keep cables curved correctly
        for c in list(self.cables):
            try:
                c.redraw()
            except tk.TclError:
                # removed
                pass
        self.root.after(120, self._tick)


# --------------------------
# Run
# --------------------------

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
