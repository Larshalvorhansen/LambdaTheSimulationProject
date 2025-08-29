import tkinter as tk
import math
from dataclasses import dataclass

# ---------------------------
# Simple circular model
# ---------------------------
# Ranges:
# - Money-like quantities: 0..10000
# - Satisfaction: 0..1
# - Tax rates: 0..1
# Notes:
# - Company salary depends on worker output.
# - Worker productive work depends on salary, satisfaction, and products&services.
# - Company & Worker each pay flat taxes on their respective tax bases.

MAX_MONEY = 10_000.0


@dataclass
class State:
    subsidies: float = 1000.0
    revenues: float = 5000.0
    satisfaction: float = 0.7  # 0..1
    products: float = 3000.0  # 0..10000
    wage_per_output: float = 0.6  # salary = wage_per_output * worker_output
    tax_rate_company: float = 0.2
    tax_rate_worker: float = 0.2

    # dynamic (computed)
    salary: float = 0.0
    worker_output: float = 0.0
    taxes_company: float = 0.0
    taxes_worker: float = 0.0


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def compute_once(s: State):
    """One pass of the model given current state."""
    # Company decides salary off last known worker_output
    salary = s.wage_per_output * s.worker_output
    salary = clamp(salary, 0, MAX_MONEY)

    # Worker productivity from salary, satisfaction, and products/services
    # Weighted, then scaled to 0..10000
    w_salary = (salary / MAX_MONEY) * 0.5
    w_satis = s.satisfaction * 0.3
    w_goods = (s.products / MAX_MONEY) * 0.2
    worker_output = MAX_MONEY * clamp(w_salary + w_satis + w_goods, 0, 1)

    # Taxes
    base_profit = (s.revenues + s.subsidies) - salary
    taxes_company = s.tax_rate_company * clamp(base_profit, 0, MAX_MONEY)
    taxes_worker = s.tax_rate_worker * clamp(salary, 0, MAX_MONEY)

    s.salary = salary
    s.worker_output = worker_output
    s.taxes_company = taxes_company
    s.taxes_worker = taxes_worker


def solve_equilibrium(s: State, iters=24):
    """Simple fixed-point iteration (good enough for this toy)."""
    # start from previous values; iterate to settle
    for _ in range(iters):
        compute_once(s)


# ---------------------------
# UI
# ---------------------------


class Port:
    def __init__(self, canvas, x, y, label, kind):
        self.canvas = canvas
        self.x, self.y = x, y
        self.kind = kind  # "in" or "out"
        self.r = 8
        self.circle = canvas.create_oval(
            x - self.r,
            y - self.r,
            x + self.r,
            y + self.r,
            fill="#111",
            outline="#ccc",
            width=2,
        )
        self.text = canvas.create_text(
            x, y - 18, text=label, fill="#ddd", font=("Arial", 10, "bold")
        )
        self.value_text = canvas.create_text(
            x, y + 18, text="", fill="#9ee", font=("Arial", 10)
        )

    def set_value(self, v, money_like=True):
        if money_like:
            txt = f"{v:,.0f}"
        else:
            txt = f"{v:.2f}"
        self.canvas.itemconfigure(self.value_text, text=txt)

    def pos(self):
        return (self.x, self.y)


class Cable:
    def __init__(self, canvas, src_port: Port, dst_port: Port, color="#2dd4bf"):
        self.canvas = canvas
        self.src = src_port
        self.dst = dst_port
        self.color = color
        self.path = canvas.create_line(
            *self._curve_points(), smooth=True, splinesteps=20, width=3, fill=color
        )

    def _curve_points(self):
        x1, y1 = self.src.pos()
        x2, y2 = self.dst.pos()
        dx = (x2 - x1) * 0.5
        c1 = (x1 + dx, y1)
        c2 = (x2 - dx, y2)
        return (x1, y1, *c1, *c2, x2, y2)

    def redraw(self, thickness=3.0):
        self.canvas.coords(self.path, *self._curve_points())
        self.canvas.itemconfigure(self.path, width=thickness)


class Block:
    def __init__(self, canvas, x, y, w, h, title):
        self.canvas = canvas
        self.rect = canvas.create_rectangle(
            x, y, x + w, y + h, fill="#1f2937", outline="#94a3b8", width=3
        )
        self.title = canvas.create_text(
            x + w / 2, y + 18, text=title, fill="#fff", font=("Arial", 14, "bold")
        )
        self.x, self.y, self.w, self.h = x, y, w, h
        self.ports_in = []
        self.ports_out = []

    def add_input(self, label, idx):
        x = self.x + 28
        y = self.y + 60 + idx * 70
        p = Port(self.canvas, x, y, label, "in")
        self.ports_in.append(p)
        return p

    def add_output(self, label, idx):
        x = self.x + self.w - 28
        y = self.y + 60 + idx * 70
        p = Port(self.canvas, x, y, label, "out")
        self.ports_out.append(p)
        return p


class App:
    def __init__(self, root):
        self.root = root
        root.title("Company X & Worker Y — simple patchable economy")
        self.state = State()

        self.canvas = tk.Canvas(
            root, width=1000, height=560, bg="#0b1220", highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Blocks
        self.company = Block(self.canvas, 110, 70, 330, 360, "Company X")
        self.worker = Block(self.canvas, 560, 70, 330, 360, "Worker Y")

        # Ports
        # Company inputs (3): subsidies, revenues, worker output
        self.p_c_subsidies = self.company.add_input("Government subsidies", 0)
        self.p_c_revenues = self.company.add_input("Revenues", 1)
        self.p_c_wout_in = self.company.add_input("Worker output", 2)
        # Company outputs (2): gov taxes, salary
        self.p_c_taxes_out = self.company.add_output("→ Gov taxes", 0)
        self.p_c_salary_out = self.company.add_output("→ Salary", 1)

        # Worker inputs (3): salary, satisfaction, products&services
        self.p_w_salary_in = self.worker.add_input("Salary", 0)
        self.p_w_satis_in = self.worker.add_input("Satisfaction", 1)
        self.p_w_goods_in = self.worker.add_input("Products & services", 2)
        # Worker outputs (2): gov taxes, productive work
        self.p_w_taxes_out = self.worker.add_output("→ Gov taxes", 0)
        self.p_w_work_out = self.worker.add_output("→ Productive work", 1)

        # Patch cables between Company and Worker
        self.cable_salary = Cable(
            self.canvas, self.p_c_salary_out, self.p_w_salary_in, color="#38bdf8"
        )
        self.cable_output = Cable(
            self.canvas, self.p_w_work_out, self.p_c_wout_in, color="#22c55e"
        )

        # Controls (sliders)
        self.sidebar = tk.Frame(root, bg="#0b1220")
        self.sidebar.grid(row=0, column=1, sticky="ns")
        self._make_sliders()

        # Footer note
        self.canvas.create_text(
            500,
            535,
            text="Flat-tax toy model • drag sliders; cables show flows",
            fill="#9ca3af",
            font=("Arial", 10),
        )

        # Animation / compute loop
        self.update_ui()

        # Resize behavior
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

    def _slider(
        self,
        parent,
        label,
        from_,
        to,
        initial,
        step,
        width=240,
        fmt=lambda v: f"{v:.0f}",
    ):
        frame = tk.Frame(parent, bg="#0b1220")
        frame.pack(anchor="w", padx=10, pady=6)
        tk.Label(
            frame, text=label, fg="white", bg="#0b1220", font=("Arial", 10, "bold")
        ).pack(anchor="w")
        s = tk.Scale(
            frame,
            from_=from_,
            to=to,
            orient="horizontal",
            resolution=step,
            length=width,
            bg="#0b1220",
            fg="white",
            troughcolor="#1f2937",
            highlightthickness=0,
        )
        s.set(initial)
        s.pack(anchor="w")
        val_lbl = tk.Label(frame, text=fmt(initial), fg="#9ee", bg="#0b1220")
        val_lbl.pack(anchor="w")

        def on_slide(v):
            val_lbl.config(text=fmt(float(v)))

        s.configure(command=on_slide)
        return s

    def _make_sliders(self):
        self.s_subsidies = self._slider(
            self.sidebar, "Government subsidies", 0, MAX_MONEY, self.state.subsidies, 50
        )
        self.s_revenues = self._slider(
            self.sidebar, "Company revenues", 0, MAX_MONEY, self.state.revenues, 50
        )
        self.s_satis = self._slider(
            self.sidebar,
            "Worker satisfaction (0–1)",
            0,
            1,
            self.state.satisfaction,
            0.01,
            fmt=lambda v: f"{float(v):.2f}",
        )
        self.s_products = self._slider(
            self.sidebar, "Products & services", 0, MAX_MONEY, self.state.products, 50
        )
        self.s_wage = self._slider(
            self.sidebar,
            "Wage per output (salary = w*output)",
            0,
            2.0,
            self.state.wage_per_output,
            0.01,
            fmt=lambda v: f"{float(v):.2f}",
        )
        self.s_tax_c = self._slider(
            self.sidebar,
            "Company flat tax rate",
            0,
            1.0,
            self.state.tax_rate_company,
            0.01,
            fmt=lambda v: f"{float(v):.2f}",
        )
        self.s_tax_w = self._slider(
            self.sidebar,
            "Worker flat tax rate",
            0,
            1.0,
            self.state.tax_rate_worker,
            0.01,
            fmt=lambda v: f"{float(v):.2f}",
        )

    def _thickness_from_value(self, v):
        # Line thickness scales gently with value 0..10000 -> 2..10
        return 2 + 8 * clamp(v / MAX_MONEY, 0, 1)

    def update_ui(self):
        # Read sliders into state
        s = self.state
        s.subsidies = float(self.s_subsidies.get())
        s.revenues = float(self.s_revenues.get())
        s.satisfaction = float(self.s_satis.get())
        s.products = float(self.s_products.get())
        s.wage_per_output = float(self.s_wage.get())
        s.tax_rate_company = float(self.s_tax_c.get())
        s.tax_rate_worker = float(self.s_tax_w.get())

        # Solve for equilibrium-ish values
        solve_equilibrium(s, iters=24)

        # Update port value labels
        # Company side
        self.p_c_subsidies.set_value(s.subsidies)
        self.p_c_revenues.set_value(s.revenues)
        self.p_c_wout_in.set_value(s.worker_output)
        self.p_c_taxes_out.set_value(s.taxes_company)
        self.p_c_salary_out.set_value(s.salary)

        # Worker side
        self.p_w_salary_in.set_value(s.salary)
        self.p_w_satis_in.set_value(s.satisfaction, money_like=False)
        self.p_w_goods_in.set_value(s.products)
        self.p_w_taxes_out.set_value(s.taxes_worker)
        self.p_w_work_out.set_value(s.worker_output)

        # Redraw cables with thickness based on flow magnitude
        self.cable_salary.redraw(thickness=self._thickness_from_value(s.salary))
        self.cable_output.redraw(thickness=self._thickness_from_value(s.worker_output))

        # Schedule next update
        self.root.after(120, self.update_ui)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
