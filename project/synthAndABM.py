import numpy as np
import matplotlib.pyplot as plt
import random
import math
import time # For pausing simulation steps

# --- Constants ---
DEFAULT_BOUNDS = [0, 100, 0, 50] # x_min, x_max, y_min, y_max for LHS
HISTORY_LENGTH = 200 # Number of time steps to show on RHS output
AGENT_SIZE = 150 # Visual size of agents on the plot
MOVEMENT_STEP = 0.5 # Max random movement per step

# --- Agent Base Class ---
class Agent:
    """ Base class for all synth modules (agents). """
    _agent_count = 0 # Class variable for unique IDs

    def __init__(self, env, pos, type_name="Generic", params=None, color=None):
        self.id = f"{type_name}_{Agent._agent_count}"
        Agent._agent_count += 1
        self.env = env # Reference to the environment
        if pos is None:
             # Assign a random position if none provided
             self.pos = np.array([
                 random.uniform(DEFAULT_BOUNDS[0]+5, DEFAULT_BOUNDS[1]-5),
                 random.uniform(DEFAULT_BOUNDS[2]+5, DEFAULT_BOUNDS[3]-5)
             ], dtype=float)
        else:
            self.pos = np.array(pos, dtype=float)

        self.type = type_name
        self.params = params if params is not None else {}
        self.state = 0.0  # Current output value of this module
        self.inputs = {}  # Dictionary to store connected input agents: {input_name: source_agent}
        self.color = color if color else random.choice(['#FF6347', '#4682B4', '#32CD32', '#FFD700', '#6A5ACD', '#FF8C00']) # Tomato, SteelBlue, LimeGreen, Gold, SlateBlue, DarkOrange

    def add_input(self, source_agent, input_name="input"):
        """ Connect an output from source_agent to a named input of this agent. """
        self.inputs[input_name] = source_agent
        print(f"Connecting {source_agent.id} -> {self.id} ({input_name})")

    def get_input_value(self, input_name="input", default=0.0):
        """ Get the current state (output value) of a connected input agent. """
        if input_name in self.inputs:
            source_agent = self.inputs[input_name]
            # In a complex system, you might need the state from the *previous* step
            # to handle feedback loops correctly. Here, we use the current state,
            # assuming an appropriate update order is handled by the environment.
            return source_agent.state
        return default # Default value if input is not connected

    def update_state(self, time_step, current_time):
        """
        Update the agent's internal state based on inputs and parameters.
        Must be implemented by subclasses.
        'time_step' is the duration since the last update.
        'current_time' is the total simulation time.
        """
        # Default behavior: output is the average of inputs (if any)
        if not self.inputs:
            self.state = 0.0
        else:
            self.state = sum(src.state for src in self.inputs.values()) / len(self.inputs)

    def move(self, bounds):
        """ Basic random movement within the environment bounds. """
        self.pos += np.random.uniform(-MOVEMENT_STEP, MOVEMENT_STEP, 2)
        # Keep within bounds
        self.pos[0] = np.clip(self.pos[0], bounds[0], bounds[1])
        self.pos[1] = np.clip(self.pos[1], bounds[2], bounds[3])

    def __repr__(self):
        return f"{self.type}({self.id})"

# --- Concrete Agent Subclasses ---

class Oscillator(Agent):
    """ Produces a periodic waveform (e.g., sine wave). """
    def __init__(self, env, pos=None, freq=1.0, amp=1.0):
        super().__init__(env, pos, "Osc", {'freq': freq, 'amp': amp}, color='#FF6347') # Tomato
        self.phase = random.uniform(0, 2 * math.pi) # Start with random phase

    def update_state(self, time_step, current_time):
        freq = self.params['freq']
        amp = self.params['amp']
        # Allow frequency modulation via 'fm' input
        fm_input = self.get_input_value("fm", default=0.0)
        modulated_freq = freq + fm_input # Simple FM
        self.state = amp * math.sin(self.phase + 2 * math.pi * modulated_freq * current_time)

class LFO(Oscillator):
    """ Low Frequency Oscillator, typically used for modulation. """
    def __init__(self, env, pos=None, freq=0.2, amp=1.0):
         # Default to lower frequency
        super().__init__(env, pos, freq=freq, amp=amp)
        self.type = "LFO" # Override type name
        self.color = '#FFD700' # Gold

class VCA(Agent):
    """ Voltage Controlled Amplifier: Modulates the amplitude of an input signal. """
    def __init__(self, env, pos=None, base_gain=0.0):
         super().__init__(env, pos, "VCA", {'base_gain': base_gain}, color='#4682B4') # SteelBlue

    def update_state(self, time_step, current_time):
        audio_in = self.get_input_value("audio_in", default=0.0)
        control_in = self.get_input_value("control_in", default=1.0) # Default to pass-through if no CV
        base_gain = self.params['base_gain']

        # Control input typically ranges from 0 to 1 (or bipolar)
        # Let's clip it to be positive for simple amplitude scaling
        effective_gain = base_gain + max(0, control_in)
        self.state = audio_in * effective_gain

class Mixer(Agent):
    """ Combines multiple input signals. """
    def __init__(self, env, pos=None, num_inputs=2, mode='average'): # mode can be 'sum' or 'average'
         super().__init__(env, pos, "Mixer", {'num_inputs': num_inputs, 'mode': mode}, color='#32CD32') # LimeGreen
         # Input names will be 'in_1', 'in_2', ...

    def update_state(self, time_step, current_time):
        total = 0.0
        connected_inputs = 0
        for i in range(1, self.params['num_inputs'] + 1):
            input_name = f"in_{i}"
            if input_name in self.inputs: # Check if this specific input is connected
                total += self.get_input_value(input_name)
                connected_inputs += 1

        if self.params['mode'] == 'average':
            self.state = total / max(1, connected_inputs) if connected_inputs > 0 else 0.0
        elif self.params['mode'] == 'sum':
            self.state = total
        else:
            self.state = 0.0 # Default for unknown mode


# --- Environment Class ---
class SynthEnvironment:
    """ Manages the agents, connections, simulation steps, and visualization. """
    def __init__(self, bounds=None, history_len=HISTORY_LENGTH, time_step=0.05):
        self.agents = {} # Use dict for easy ID lookup: {id: agent}
        self.connections = [] # Store as (source_agent_id, target_agent_id, target_input_name)
        self.bounds = bounds if bounds is not None else DEFAULT_BOUNDS
        self.current_time = 0.0
        self.time_step = time_step # Simulation time granularity
        self.history_len = history_len
        self.output_history = []
        self.output_agent_id = None # ID of the agent whose state is plotted on RHS

        self.fig = None
        self.ax_lhs = None
        self.ax_rhs = None
        self.agent_scatter = None
        self.agent_labels = []
        self.cable_lines = []
        self.output_line = None

    def add_agent(self, agent):
        """ Adds an agent instance to the environment. """
        if agent.id in self.agents:
            raise ValueError(f"Agent with ID {agent.id} already exists.")
        self.agents[agent.id] = agent
        print(f"Added Agent: {agent.id} at {agent.pos}")

    def add_connection(self, source_id, target_id, target_input_name="input"):
        """ Creates a connection (cable) between two agents. """
        if source_id not in self.agents or target_id not in self.agents:
            print(f"Warning: Cannot connect {source_id} -> {target_id}. Agent not found.")
            return
        source_agent = self.agents[source_id]
        target_agent = self.agents[target_id]
        target_agent.add_input(source_agent, target_input_name)
        self.connections.append((source_id, target_id, target_input_name))

    def set_output_agent(self, agent_id):
        """ Designates an agent as the final output for the RHS plot. """
        if agent_id not in self.agents:
             raise ValueError(f"Cannot set output: Agent ID {agent_id} not found.")
        self.output_agent_id = agent_id
        print(f"Set Output Agent: {agent_id}")

    def get_update_order(self):
        """
        Determines the order agents should be updated based on dependencies.
        Simple strategy: Oscillators/LFOs first, then others.
        A more robust solution would use topological sort, especially for complex graphs.
        """
        # Basic order: sources (Osc, LFO) -> processors (VCA) -> sinks (Mixer)
        order = sorted(self.agents.values(), key=lambda a: (
            0 if isinstance(a, (Oscillator, LFO)) else # Sources first
            1 if isinstance(a, VCA) else           # Then processors
            2 if isinstance(a, Mixer) else         # Then sinks/combiners
            5 # Others later
        ))
        # print("Update order:", [a.id for a in order]) # Debug
        return order

    def step(self):
        """ Performs one simulation step. """
        # 1. Update Agent States in a determined order
        update_order = self.get_update_order()
        for agent in update_order:
            agent.update_state(self.time_step, self.current_time)

        # 2. Move Agents
        for agent in self.agents.values():
            agent.move(self.bounds)

        # 3. Record Output History
        output_value = 0.0 # Default if no output agent set
        if self.output_agent_id and self.output_agent_id in self.agents:
            output_value = self.agents[self.output_agent_id].state

        self.output_history.append(output_value)
        # Keep history buffer at fixed length
        if len(self.output_history) > self.history_len:
            self.output_history.pop(0)

        # 4. Increment Time
        self.current_time += self.time_step

    def setup_visualization(self):
        """ Initializes the matplotlib figure and axes. """
        plt.ion() # Turn interactive mode on
        self.fig = plt.figure(figsize=(14, 7))
        gs = self.fig.add_gridspec(1, 2, width_ratios=[2, 1]) # Make LHS wider

        # --- LHS: Synth Rack ---
        self.ax_lhs = self.fig.add_subplot(gs[0])
        self.ax_lhs.set_xlim(self.bounds[0], self.bounds[1])
        self.ax_lhs.set_ylim(self.bounds[2], self.bounds[3])
        self.ax_lhs.set_title("Synth Rack (Agents & Dependencies)")
        self.ax_lhs.set_xlabel("X Position")
        self.ax_lhs.set_ylabel("Y Position")
        self.ax_lhs.set_xticks(np.linspace(self.bounds[0], self.bounds[1], 5))
        self.ax_lhs.set_yticks(np.linspace(self.bounds[2], self.bounds[3], 3))
        self.ax_lhs.grid(True, linestyle=':', alpha=0.7)

        # Placeholders for plot elements
        self.agent_scatter = self.ax_lhs.scatter([], [], s=AGENT_SIZE, c=[], alpha=0.8, edgecolors='k')
        # agent_labels and cable_lines lists will be managed in update_visualization

        # --- RHS: Output ---
        self.ax_rhs = self.fig.add_subplot(gs[1])
        self.ax_rhs.set_xlim(0, self.history_len)
        self.ax_rhs.set_ylim(-1.5, 1.5) # Initial reasonable range
        self.ax_rhs.set_title("System Output")
        self.ax_rhs.set_xlabel(f"Time Steps (Last {self.history_len})")
        self.ax_rhs.set_ylabel("Value")
        self.ax_rhs.grid(True, linestyle=':', alpha=0.7)
        self.output_line, = self.ax_rhs.plot([], [], 'b-') # Blue line for output

        plt.tight_layout()
        plt.show()


    def update_visualization(self):
        """ Updates the plot with current agent positions, connections, and output. """
        if self.fig is None: return # Don't draw if not setup

        # --- Update LHS ---
        # Agents (dots)
        positions = np.array([agent.pos for agent in self.agents.values()])
        colors = [agent.color for agent in self.agents.values()]
        if positions.size > 0:
            self.agent_scatter.set_offsets(positions)
            self.agent_scatter.set_facecolors(colors) # Use facecolors for fill

        # Labels (text) - remove old, add new
        for label in self.agent_labels:
            label.remove()
        self.agent_labels.clear()
        for agent_id, agent in self.agents.items():
            label = self.ax_lhs.text(agent.pos[0], agent.pos[1] + 2, f"{agent.type}\n({agent_id})",
                                     fontsize=7, ha='center', va='bottom',
                                     bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3))
            self.agent_labels.append(label)

        # Cables (lines) - remove old, add new
        for line in self.cable_lines:
            line.remove()
        self.cable_lines.clear()
        for src_id, tgt_id, _ in self.connections:
            if src_id in self.agents and tgt_id in self.agents:
                src_pos = self.agents[src_id].pos
                tgt_pos = self.agents[tgt_id].pos
                line, = self.ax_lhs.plot([src_pos[0], tgt_pos[0]], [src_pos[1], tgt_pos[1]],
                                        color='grey', linestyle='-', linewidth=1.5, alpha=0.6)
                # Add a small marker to indicate direction (optional)
                # dx = tgt_pos[0] - src_pos[0]
                # dy = tgt_pos[1] - src_pos[1]
                # midpoint_x = src_pos[0] + dx * 0.55
                # midpoint_y = src_pos[1] + dy * 0.55
                # arrow = self.ax_lhs.plot(midpoint_x, midpoint_y, marker='>', markersize=4, color='grey', alpha=0.6, linestyle='')
                # self.cable_lines.extend([line, arrow[0]]) # Add both line and marker
                self.cable_lines.append(line)


        # --- Update RHS ---
        # Output Waveform
        history = self.output_history
        x_data = np.arange(len(history))
        self.output_line.set_data(x_data, history)

        # Adjust y-axis limits dynamically based on visible data
        if history:
            min_val, max_val = min(history), max(history)
            padding = (max_val - min_val) * 0.1 + 0.1 # Add small padding, ensure non-zero
            self.ax_rhs.set_ylim(min_val - padding, max_val + padding)
        else:
            self.ax_rhs.set_ylim(-1.5, 1.5) # Default if no history yet

        self.ax_rhs.set_xlim(0, max(self.history_len, len(history))) # Ensure xlim covers history

        # --- Redraw ---
        try:
            self.fig.canvas.draw()
            self.fig.canvas.flush_events() # Process GUI events for responsiveness
        except Exception as e:
            print(f"Error during plot update: {e}")
            # This can happen if the plot window is closed manually

    def run(self, num_steps, viz_update_rate=1, pause_duration=0.01):
        """ Runs the simulation loop and visualization. """
        self.setup_visualization()

        for i in range(num_steps):
            if not plt.fignum_exists(self.fig.number): # Stop if plot window closed
                 print("Plot window closed, stopping simulation.")
                 break

            self.step()

            if i % viz_update_rate == 0:
                self.update_visualization()
                plt.pause(pause_duration) # Crucial pause for plot update and interaction

        plt.ioff() # Turn interactive mode off when done
        print("Simulation finished.")
        if plt.fignum_exists(self.fig.number):
            print("Close the plot window to exit.")
            plt.show() # Keep the final plot window open until manually closed


# --- Simulation Setup Example ---
if __name__ == "__main__":
    env = SynthEnvironment(time_step=0.05, history_len=150)

    # Create Agents (Modules) - positions can be specified or None for random
    osc1 = Oscillator(env=env, pos=[15, 35], freq=1.0, amp=1.0)
    lfo1 = LFO(env=env, pos=[15, 15], freq=0.3, amp=0.8) # Modulates VCA gain
    vca1 = VCA(env=env, pos=[50, 25], base_gain=0.1)
    osc2 = Oscillator(env=env, pos=[35, 40], freq=0.7, amp=0.6) # Another sound source
    lfo2 = LFO(env=env, pos=[35, 10], freq=2.5, amp=0.2) # Modulates osc2 frequency (FM)

    # Final mixer - increase number of inputs if needed
    mixer1 = Mixer(env=env, pos=[80, 25], num_inputs=2, mode='average')

    # Add Agents to Environment
    env.add_agent(osc1)
    env.add_agent(lfo1)
    env.add_agent(vca1)
    env.add_agent(osc2)
    env.add_agent(lfo2)
    env.add_agent(mixer1)

    # Create Connections (Cables)
    # LFO1 controls VCA gain
    env.add_connection(source_id=lfo1.id, target_id=vca1.id, target_input_name='control_in')
    # Osc1 feeds audio into VCA
    env.add_connection(source_id=osc1.id, target_id=vca1.id, target_input_name='audio_in')

    # LFO2 modulates Osc2 frequency
    env.add_connection(source_id=lfo2.id, target_id=osc2.id, target_input_name='fm')

    # VCA output goes to Mixer input 1
    env.add_connection(source_id=vca1.id, target_id=mixer1.id, target_input_name='in_1')
    # Osc2 output goes to Mixer input 2
    env.add_connection(source_id=osc2.id, target_id=mixer1.id, target_input_name='in_2')

    # Specify the final output agent for the RHS plot
    env.set_output_agent(mixer1.id)

    # Run Simulation
    env.run(num_steps=1000, viz_update_rate=1, pause_duration=0.01)
