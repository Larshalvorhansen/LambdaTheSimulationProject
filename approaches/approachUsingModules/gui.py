import tkinter as tk

class DraggableSquare:
    def __init__(self, canvas, x, y, size):
        self.canvas = canvas
        self.size = size
        self.shape = canvas.create_rectangle(x, y, x+size, y+size, fill='red')
        self.input_wire_point = (x, y + size / 2)
        self.output_wire_point = (x + size, y + size / 2)
        self.connected_lines = []
        self.offset_x = 0
        self.offset_y = 0
        
        self.canvas.tag_bind(self.shape, '<Button-1>', self.on_click)
        self.canvas.tag_bind(self.shape, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.shape, '<ButtonRelease-1>', self.on_release)

    def on_click(self, event):
        self.offset_x = self.canvas.canvasx(event.x) - self.canvas.coords(self.shape)[0]
        self.offset_y = self.canvas.canvasy(event.y) - self.canvas.coords(self.shape)[1]

    def on_drag(self, event):
        x, y = self.canvas.canvasx(event.x) - self.offset_x, self.canvas.canvasy(event.y) - self.offset_y
        self.canvas.coords(self.shape, x, y, x + self.size, y + self.size)
        self.update_wires()

    def on_release(self, event):
        # Attempt to connect wire to nearest block's input
        for block in self.canvas.blocks:
            if block is not self:
                block_input_x, block_input_y = block.input_wire_point
                if abs(event.x - block_input_x) < 10 and abs(event.y - block_input_y) < 10:
                    self.connect_to(block)

    def update_wires(self):
        for line, target_block in self.connected_lines:
            x1, y1 = self.output_wire_point
            x2, y2 = target_block.input_wire_point
            self.canvas.coords(line, x1, y1, x2, y2)

    def connect_to(self, block):
        x1, y1 = self.output_wire_point
        x2, y2 = block.input_wire_point
        line = self.canvas.create_line(x1, y1, x2, y2, fill="blue", dash=(4, 2))
        self.connected_lines.append((line, block))

class WireCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocks = []

    def add_block(self, x, y, size):
        block = DraggableSquare(self, x, y, size)
        self.blocks.append(block)

def main():
    root = tk.Tk()
    root.title("Drag & Drop Red Squares with Wires")
    
    canvas = WireCanvas(root, width=800, height=600)
    canvas.pack()
    
    # Create blocks
    canvas.add_block(20, 20, 50)
    canvas.add_block(200, 100, 50)
    canvas.add_block(400, 200, 50)
    
    root.mainloop()

if __name__ == '__main__':
    main()
