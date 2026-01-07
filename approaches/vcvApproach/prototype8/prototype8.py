"""
System Dynamics Node-Based Simulation Platform
Core prototype with node editor, simulation engine, and real-time plotting
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QDockWidget,
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QFont
import pyqtgraph as pg


# ============================================================================
# NODE SYSTEM - Core computation classes
# ============================================================================


class Port:
    """Represents an input or output port on a node"""

    def __init__(self, node, name, is_output=False):
        self.node = node
        self.name = name
        self.is_output = is_output
        self.connections = []  # List of connected ports
        self.value = 0.0

    def connect_to(self, other_port):
        """Connect this port to another port"""
        if self.is_output and not other_port.is_output:
            self.connections.append(other_port)
            other_port.connections.append(self)
            return True
        return False

    def get_value(self):
        """Get the current value at this port"""
        if self.is_output:
            return self.value
        elif self.connections:
            # Input port gets value from connected output
            return self.connections[0].value
        return 0.0


class Node:
    """Base class for all computational nodes"""

    def __init__(self, name):
        self.name = name
        self.inputs = {}
        self.outputs = {}
        self.state = {}  # For stateful nodes (integrators, etc.)

    def add_input(self, name):
        self.inputs[name] = Port(self, name, is_output=False)

    def add_output(self, name):
        self.outputs[name] = Port(self, name, is_output=True)

    def compute(self, dt=0.01):
        """Override this method to implement node computation"""
        pass

    def reset(self):
        """Reset any internal state"""
        self.state = {}


# ============================================================================
# CONCRETE NODE TYPES
# ============================================================================


class ConstantNode(Node):
    """Outputs a constant value"""

    def __init__(self, name="Constant", value=1.0):
        super().__init__(name)
        self.add_output("out")
        self.constant_value = value

    def compute(self, dt=0.01):
        self.outputs["out"].value = self.constant_value


class AddNode(Node):
    """Adds two inputs"""

    def __init__(self, name="Add"):
        super().__init__(name)
        self.add_input("a")
        self.add_input("b")
        self.add_output("out")

    def compute(self, dt=0.01):
        a = self.inputs["a"].get_value()
        b = self.inputs["b"].get_value()
        self.outputs["out"].value = a + b


class MultiplyNode(Node):
    """Multiplies two inputs"""

    def __init__(self, name="Multiply"):
        super().__init__(name)
        self.add_input("a")
        self.add_input("b")
        self.add_output("out")

    def compute(self, dt=0.01):
        a = self.inputs["a"].get_value()
        b = self.inputs["b"].get_value()
        self.outputs["out"].value = a * b


class IntegratorNode(Node):
    """Integrates input over time (dx/dt = input)"""

    def __init__(self, name="Integrator", initial_value=0.0):
        super().__init__(name)
        self.add_input("in")
        self.add_output("out")
        self.state["value"] = initial_value
        self.initial_value = initial_value

    def compute(self, dt=0.01):
        derivative = self.inputs["in"].get_value()
        self.state["value"] += derivative * dt
        self.outputs["out"].value = self.state["value"]

    def reset(self):
        self.state["value"] = self.initial_value


class GainNode(Node):
    """Multiplies input by a constant gain"""

    def __init__(self, name="Gain", gain=1.0):
        super().__init__(name)
        self.add_input("in")
        self.add_output("out")
        self.gain = gain

    def compute(self, dt=0.01):
        self.outputs["out"].value = self.inputs["in"].get_value() * self.gain


# ============================================================================
# GRAPHICS - Visual representation of nodes
# ============================================================================


class GraphicsPort(QGraphicsEllipseItem):
    """Visual representation of a port"""

    def __init__(self, port, parent, is_output=False):
        super().__init__(-5, -5, 10, 10, parent)
        self.port = port
        self.is_output = is_output
        self.setBrush(
            QBrush(QColor(100, 200, 100) if is_output else QColor(200, 100, 100))
        )
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def hoverEnterEvent(self, event):
        self.setBrush(
            QBrush(QColor(150, 255, 150) if self.is_output else QColor(255, 150, 150))
        )

    def hoverLeaveEvent(self, event):
        self.setBrush(
            QBrush(QColor(100, 200, 100) if self.is_output else QColor(200, 100, 100))
        )


class GraphicsNode(QGraphicsItem):
    """Visual representation of a computation node"""

    def __init__(self, node, scene):
        super().__init__()
        self.node = node
        self.scene_ref = scene
        self.width = 120
        self.height = 60
        self.port_graphics = {}

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # Create visual ports
        input_spacing = self.height / (len(node.inputs) + 1)
        for i, (name, port) in enumerate(node.inputs.items()):
            port_graphic = GraphicsPort(port, self, is_output=False)
            port_graphic.setPos(0, (i + 1) * input_spacing)
            self.port_graphics[port] = port_graphic

        output_spacing = self.height / (len(node.outputs) + 1)
        for i, (name, port) in enumerate(node.outputs.items()):
            port_graphic = GraphicsPort(port, self, is_output=True)
            port_graphic.setPos(self.width, (i + 1) * output_spacing)
            self.port_graphics[port] = port_graphic

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        # Draw shadow for depth
        shadow_offset = 3
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))
        painter.drawRoundedRect(
            shadow_offset, shadow_offset, self.width, self.height, 5, 5
        )

        # Draw node body
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 200, 0), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))

        # Color code by node type
        node_type = type(self.node).__name__
        if "Integrator" in node_type:
            color = QColor(80, 120, 180)  # Blue for integrators
        elif "Constant" in node_type:
            color = QColor(100, 140, 100)  # Green for constants
        elif "Gain" in node_type:
            color = QColor(140, 100, 140)  # Purple for gains
        else:
            color = QColor(100, 100, 120)  # Gray for others

        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)

        # Draw node name
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(
            QRectF(0, 0, self.width, self.height),
            Qt.AlignmentFlag.AlignCenter,
            self.node.name,
        )

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update connection lines when node moves
            self.scene_ref.update_connections()
        return super().itemChange(change, value)

    def get_port_scene_pos(self, port):
        """Get the scene position of a port"""
        if port in self.port_graphics:
            port_graphic = self.port_graphics[port]
            return self.mapToScene(port_graphic.pos())
        return QPointF(0, 0)


class ConnectionLine(QGraphicsLineItem):
    """Visual representation of a connection between ports"""

    def __init__(self, from_port, to_port, from_node_graphic, to_node_graphic):
        super().__init__()
        self.from_port = from_port
        self.to_port = to_port
        self.from_node = from_node_graphic
        self.to_node = to_node_graphic

        self.setPen(QPen(QColor(150, 150, 200), 3))
        self.setZValue(-1)
        self.update_position()

    def update_position(self):
        """Update line position based on node positions"""
        p1 = self.from_node.get_port_scene_pos(self.from_port)
        p2 = self.to_node.get_port_scene_pos(self.to_port)
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())


# ============================================================================
# SCENE AND VIEW
# ============================================================================


class NodeEditorScene(QGraphicsScene):
    """Scene that manages nodes and connections"""

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.node_graphics = {}
        self.connections = []

        self.setSceneRect(-2000, -2000, 4000, 4000)
        self.setBackgroundBrush(QBrush(QColor(40, 40, 45)))

    def drawBackground(self, painter, rect):
        """Draw grid background"""
        super().drawBackground(painter, rect)

        # Draw grid
        left = int(rect.left()) - (int(rect.left()) % 50)
        top = int(rect.top()) - (int(rect.top()) % 50)

        lines = []
        for x in range(left, int(rect.right()), 50):
            lines.append(QPointF(x, rect.top()))
            lines.append(QPointF(x, rect.bottom()))

        for y in range(top, int(rect.bottom()), 50):
            lines.append(QPointF(rect.left(), y))
            lines.append(QPointF(rect.right(), y))

        painter.setPen(QPen(QColor(60, 60, 65), 1))
        for i in range(0, len(lines), 2):
            painter.drawLine(lines[i], lines[i + 1])

    def add_node(self, node, position=None):
        """Add a node to the scene"""
        graphic = GraphicsNode(node, self)
        if position:
            graphic.setPos(position)
        else:
            graphic.setPos(len(self.nodes) * 150, len(self.nodes) * 100)

        self.addItem(graphic)
        self.nodes.append(node)
        self.node_graphics[node] = graphic
        return graphic

    def connect_nodes(self, from_node, from_port_name, to_node, to_port_name):
        """Create a connection between two nodes"""
        from_port = from_node.outputs.get(from_port_name)
        to_port = to_node.inputs.get(to_port_name)

        if from_port and to_port and from_port.connect_to(to_port):
            from_graphic = self.node_graphics[from_node]
            to_graphic = self.node_graphics[to_node]

            connection = ConnectionLine(from_port, to_port, from_graphic, to_graphic)
            self.addItem(connection)
            self.connections.append(connection)
            return True
        return False

    def update_connections(self):
        """Update all connection line positions"""
        for conn in self.connections:
            conn.update_position()


class NodeEditorView(QGraphicsView):
    """View for the node editor"""

    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Center on content initially
        self.centerOn(500, 100)

    def wheelEvent(self, event):
        """Zoom with mouse wheel"""
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.scale(factor, factor)


# ============================================================================
# SIMULATION ENGINE
# ============================================================================


class SimulationEngine:
    """Executes node graph computations"""

    def __init__(self, nodes):
        self.nodes = nodes
        self.time = 0.0
        self.dt = 0.01
        self.history = {}  # Store time series data
        self.max_history = 1000

    def reset(self):
        """Reset simulation state"""
        self.time = 0.0
        self.history = {}
        for node in self.nodes:
            node.reset()

    def step(self):
        """Execute one simulation step"""
        # Compute all nodes (simplified - doesn't handle execution order)
        for node in self.nodes:
            node.compute(self.dt)

        # Store history
        for node in self.nodes:
            node_id = id(node)
            if node_id not in self.history:
                self.history[node_id] = {"time": [], "values": {}}

            self.history[node_id]["time"].append(self.time)
            for name, port in node.outputs.items():
                if name not in self.history[node_id]["values"]:
                    self.history[node_id]["values"][name] = []
                self.history[node_id]["values"][name].append(port.value)

                # Limit history size
                if len(self.history[node_id]["values"][name]) > self.max_history:
                    self.history[node_id]["values"][name].pop(0)
                    if len(self.history[node_id]["time"]) > self.max_history:
                        self.history[node_id]["time"].pop(0)

        self.time += self.dt


# ============================================================================
# MAIN APPLICATION
# ============================================================================


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Dynamics Node Editor")
        self.setGeometry(100, 100, 1400, 800)

        # Create scene and view
        self.scene = NodeEditorScene()
        self.view = NodeEditorView(self.scene)

        # Create simulation engine
        self.sim_engine = None
        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(self.simulation_step)
        self.is_running = False

        # Setup UI
        self.setup_ui()

        # Create demo system
        self.create_demo_system()

    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Control panel
        control_layout = QHBoxLayout()

        self.run_btn = QPushButton("▶ Run")
        self.run_btn.clicked.connect(self.toggle_simulation)
        control_layout.addWidget(self.run_btn)

        self.reset_btn = QPushButton("⟲ Reset")
        self.reset_btn.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.reset_btn)

        self.time_label = QLabel("Time: 0.00s")
        control_layout.addWidget(self.time_label)

        help_label = QLabel("💡 Drag nodes • Scroll to zoom • Drag background to pan")
        help_label.setStyleSheet("color: #888; font-style: italic;")
        control_layout.addWidget(help_label)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Node editor view
        layout.addWidget(self.view, stretch=1)

        # Plot widget
        self.setup_plot_widget()

    def setup_plot_widget(self):
        """Setup the plotting widget"""
        plot_dock = QDockWidget("Output Plot", self)
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground("w")
        plot_widget.setLabel("left", "Value")
        plot_widget.setLabel("bottom", "Time", units="s")
        plot_widget.addLegend()

        self.plot_widget = plot_widget
        self.plot_curves = {}

        plot_dock.setWidget(plot_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, plot_dock)

    def create_demo_system(self):
        """Create a demo system: simple oscillator"""
        # Create nodes
        const = ConstantNode("Input", value=1.0)
        gain1 = GainNode("Spring K", gain=-1.0)
        gain2 = GainNode("Damping", gain=-0.1)
        add = AddNode("Sum Forces")
        integrator1 = IntegratorNode("Velocity", initial_value=0.0)
        integrator2 = IntegratorNode("Position", initial_value=1.0)

        # Add to scene
        self.scene.add_node(const, QPointF(50, 100))
        self.scene.add_node(gain1, QPointF(400, 50))
        self.scene.add_node(gain2, QPointF(400, 150))
        self.scene.add_node(add, QPointF(600, 100))
        self.scene.add_node(integrator1, QPointF(800, 100))
        self.scene.add_node(integrator2, QPointF(1000, 100))

        # Connect nodes - simple spring-damper system
        self.scene.connect_nodes(integrator2, "out", gain1, "in")  # Position feedback
        self.scene.connect_nodes(integrator1, "out", gain2, "in")  # Velocity damping
        self.scene.connect_nodes(gain1, "out", add, "a")
        self.scene.connect_nodes(gain2, "out", add, "b")
        self.scene.connect_nodes(add, "out", integrator1, "in")
        self.scene.connect_nodes(integrator1, "out", integrator2, "in")

        # Initialize simulation engine
        self.sim_engine = SimulationEngine(self.scene.nodes)

        # Setup plot curves
        colors = ["r", "b", "g", "m", "c", "y"]
        for i, node in enumerate([integrator2, integrator1]):
            color = colors[i % len(colors)]
            curve = self.plot_widget.plot(pen=color, name=node.name)
            self.plot_curves[id(node)] = curve

    def toggle_simulation(self):
        """Start or stop the simulation"""
        if self.is_running:
            self.sim_timer.stop()
            self.run_btn.setText("▶ Run")
            self.is_running = False
        else:
            self.sim_timer.start(20)  # 50 Hz update rate
            self.run_btn.setText("⏸ Pause")
            self.is_running = True

    def reset_simulation(self):
        """Reset the simulation"""
        was_running = self.is_running
        if self.is_running:
            self.toggle_simulation()

        if self.sim_engine:
            self.sim_engine.reset()
            self.time_label.setText("Time: 0.00s")

            # Clear plots
            for curve in self.plot_curves.values():
                curve.setData([], [])

    def simulation_step(self):
        """Execute one simulation step and update display"""
        if self.sim_engine:
            # Run multiple steps for smoother simulation
            for _ in range(5):
                self.sim_engine.step()

            # Update time display
            self.time_label.setText(f"Time: {self.sim_engine.time:.2f}s")

            # Update plots
            for node_id, curve in self.plot_curves.items():
                if node_id in self.sim_engine.history:
                    hist = self.sim_engine.history[node_id]
                    if hist["time"] and "out" in hist["values"]:
                        curve.setData(hist["time"], hist["values"]["out"])


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
