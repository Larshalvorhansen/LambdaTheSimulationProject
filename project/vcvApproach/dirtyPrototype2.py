import tkinter as tk

# ------------------------
# Core Data Structures
# ------------------------


class Port:
    def __init__(self, block, name, kind, x, y):
        self.block = block
        self.name = name
        self.kind = kind  # "in" or "out"
        self.x, self.y = x, y
        self.value = 0.0
        self.circle = None
        self.value_text = None

    def pos(self):
        bx, by = self.block.x, self.block.y
        return bx + self.x, by + self.y


class Cable:
    def __init__(self, canvas, src, dst):
        self.canvas = canvas
        self.src = src
        self.dst = dst
        self.line = canvas.create_line(
            *self.points(), smooth=True, width=2, fill="cyan"
        )
        self.canvas.tag_bind(self.line, "<Button-3>", self.remove)

    def points(self):
        x1, y1 = self.src.pos()
        x2, y2 = self.dst.pos()
        return (x1, y1, (x1 + x2) // 2, y1, (x1 + x2) // 2, y2, x2, y2)

    def redraw(self):
        self.canvas.coords(self.line, *self.points())

    def remove(self, event=None):
        self.canvas.delete(self.line)
        self.canvas.master.app.connections.remove(self)


class Block:
    def __init__(self, canvas, x, y, w, h, title):
        self.canvas = canvas
        self.x, self.y, self.w, self.h = x, y, w, h
        self.title = title
        self.rect = canvas.create_rectangle(
            x, y, x + w, y + h, fill="#222", outline="#aaa", width=2
        )
        self.text = canvas.create_text(
            x + w / 2, y + 15, text=title, fill="white", font=("Arial", 12, "bold")
        )
        self.inputs = []
        self.outputs = []

    def add_input(self, name, yoff):
        p = Port(self, name, "in", 15, yoff)
        self.inputs.append(p)
        return p

    def add_output(self, name, yoff):
        p = Port(self, name, "out", self.w - 15, yoff)
        self.outputs.append(p)
        return p

    def draw_ports(self):
        for p in self.inputs + self.outputs:
            x, y = p.pos()
            color = "red" if p.kind == "in" else "green"
            if p.circle is None:
                p.circle = self.canvas.create_oval(
                    x - 6, y - 6, x + 6, y + 6, fill=color
                )
                self.canvas.tag_bind(
                    p.circle,
                    "<Button-1>",
                    lambda e, port=p: self.canvas.master.app.start_connection(port),
                )
            else:
                self.canvas.coords(p.circle, x - 6, y - 6, x + 6, y + 6)
            if p.value_text is None:
                p.value_text = self.canvas.create_text(
                    x, y - 15, text="0", fill="white", font=("Arial", 8)
                )
            self.canvas.itemconfigure(p.value_text, text=f"{p.value:.1f}")

    def compute_outputs(self):
        """Override in subclasses"""
        return {}


# ------------------------
# Block Implementations
# ------------------------


class Company(Block):
    def compute_outputs(self):
        # Inputs
        subsidies = self.inputs[0].value
        revenues = self.inputs[1].value
        worker_output = self.inputs[2].value
        # Outputs
        salary = 0.6 * worker_output
        taxes = 0.2 * max(0, revenues + subsidies - salary)
        return {"Gov taxes": taxes, "Salary": salary}


class Worker(Block):
    def compute_outputs(self):
        salary = self.inputs[0].value
        satisfaction = self.inputs[1].value
        goods = self.inputs[2].value
        productive_work = (
            salary / 10000 * 0.5 + satisfaction * 0.3 + goods / 10000 * 0.2
        ) * 10000
        taxes = 0.2 * salary
        return {"Gov taxes": taxes, "Productive work": productive_work}


# ------------------------
# Main App
# ------------------------


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Economic Modular Synth")
        self.canvas = tk.Canvas(root, width=900, height=500, bg="#111")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.master.app = self

        self.blocks = []
        self.connections = []

        # Blocks
        self.company = Company(self.canvas, 100, 100, 250, 200, "Company X")
        self.company.add_input("Subsidies", 60)
        self.company.add_input("Revenues", 110)
        self.company.add_input("Worker output", 160)
        self.company.add_output("Gov taxes", 80)
        self.company.add_output("Salary", 140)

        self.worker = Worker(self.canvas, 500, 100, 250, 200, "Worker Y")
        self.worker.add_input("Salary", 60)
        self.worker.add_input("Satisfaction", 110)
        self.worker.add_input("Goods", 160)
        self.worker.add_output("Gov taxes", 80)
        self.worker.add_output("Productive work", 140)

        self.blocks = [self.company, self.worker]

        # For creating cables
        self.dragging_port = None
        self.temp_line = None

        self.update_loop()

    # --------------------
    # Connection Handling
    # --------------------

    def start_connection(self, port):
        if port.kind == "out":
            self.dragging_port = port
            x, y = port.pos()
            self.temp_line = self.canvas.create_line(
                x, y, x, y, fill="yellow", dash=(4, 2)
            )
            self.canvas.bind("<Motion>", self.update_temp_line)
            self.canvas.bind("<ButtonRelease-1>", self.finish_connection)

    def update_temp_line(self, event):
        if self.temp_line and self.dragging_port:
            x0, y0 = self.dragging_port.pos()
            self.canvas.coords(self.temp_line, x0, y0, event.x, event.y)

    def finish_connection(self, event):
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None
        if not self.dragging_port:
            return
        # Check if released over input port
        for b in self.blocks:
            for p in b.inputs:
                x, y = p.pos()
                if (x - 8 <= event.x <= x + 8) and (y - 8 <= event.y <= y + 8):
                    # Make connection
                    c = Cable(self.canvas, self.dragging_port, p)
                    self.connections.append(c)
        self.dragging_port = None

    # --------------------
    # Simulation
    # --------------------

    def update_loop(self):
        # Reset input values
        for b in self.blocks:
            for p in b.inputs:
                p.value = 0.0

        # Aggregate inputs from connections
        for c in self.connections:
            c.redraw()
            val = c.src.value
            c.dst.value += val

        # Compute outputs for each block
        for b in self.blocks:
            results = b.compute_outputs()
            for outp, port in zip(results.values(), b.outputs):
                port.value = outp

        # Update port drawings
        for b in self.blocks:
            b.draw_ports()

        self.root.after(200, self.update_loop)


# ------------------------
# Run
# ------------------------

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
