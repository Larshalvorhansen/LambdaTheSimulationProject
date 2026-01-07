import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import solve_ivp

# Constants
g = 9.81  # gravity (m/s^2)
L1 = 1.0  # length of first pendulum (m)
L2 = 1.0  # length of second pendulum (m)
m1 = 1.0  # mass of first pendulum (kg)
m2 = 1.0  # mass of second pendulum (kg)

# Initial conditions (angles in radians and angular velocities)
theta1_0 = np.pi / 2  # initial angle of first pendulum
theta2_0 = np.pi / 2  # initial angle of second pendulum
omega1_0 = 0.0        # initial angular velocity of first pendulum
omega2_0 = 0.0        # initial angular velocity of second pendulum

# Time parameters
t_max = 20.0  # total simulation time (s)
dt = 0.05     # time step (s)
t = np.arange(0, t_max, dt)

def derivatives(t, y):
    """Calculate derivatives for the double pendulum system"""
    theta1, omega1, theta2, omega2 = y
    
    # Equations of motion for double pendulum
    delta = theta2 - theta1
    den1 = (m1 + m2) * L1 - m2 * L1 * np.cos(delta) * np.cos(delta)
    den2 = (L2 / L1) * den1
    
    # Derivatives
    dtheta1 = omega1
    domega1 = ((m2 * L1 * omega1 * omega1 * np.sin(delta) * np.cos(delta) +
               m2 * g * np.sin(theta2) * np.cos(delta) +
               m2 * L2 * omega2 * omega2 * np.sin(delta) -
               (m1 + m2) * g * np.sin(theta1)) / den1)
    
    dtheta2 = omega2
    domega2 = ((-m2 * L2 * omega2 * omega2 * np.sin(delta) * np.cos(delta) +
               (m1 + m2) * g * np.sin(theta1) * np.cos(delta) -
               (m1 + m2) * L1 * omega1 * omega1 * np.sin(delta) -
               (m1 + m2) * g * np.sin(theta2)) / den2)
    
    return [dtheta1, domega1, dtheta2, domega2]

# Solve the differential equations
sol = solve_ivp(derivatives, [0, t_max], 
                [theta1_0, omega1_0, theta2_0, omega2_0], 
                t_eval=t, rtol=1e-6, atol=1e-6)

theta1 = sol.y[0]
theta2 = sol.y[2]

# Convert angles to Cartesian coordinates
x1 = L1 * np.sin(theta1)
y1 = -L1 * np.cos(theta1)
x2 = x1 + L2 * np.sin(theta2)
y2 = y1 - L2 * np.cos(theta2)

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-(L1 + L2 + 0.1), L1 + L2 + 0.1)
ax.set_ylim(-(L1 + L2 + 0.1), L1 + L2 + 0.1)
ax.set_aspect('equal')
ax.grid()

# Create lines for the pendulums
line, = ax.plot([], [], 'o-', lw=2, color='black')
trace, = ax.plot([], [], '-', lw=1, color='red', alpha=0.5)

# Store the trace of the second pendulum
trace_x = []
trace_y = []

def init():
    line.set_data([], [])
    trace.set_data([], [])
    return line, trace

def update(frame):
    # Update pendulum line
    line.set_data([0, x1[frame], x2[frame]], [0, y1[frame], y2[frame]])
    
    # Update trace
    trace_x.append(x2[frame])
    trace_y.append(y2[frame])
    trace.set_data(trace_x, trace_y)
    
    return line, trace

# Create animation
ani = FuncAnimation(fig, update, frames=len(t), 
                    init_func=init, blit=True, interval=dt*1000)

plt.title('Double Pendulum Simulation')
plt.show()
