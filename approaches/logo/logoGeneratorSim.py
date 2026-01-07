import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random

# Number of nodes
num_nodes = 13

# Create a half-circular layout for the nodes (top half of the circle)
angles = np.linspace(0, 2* np.pi, num_nodes, endpoint=False).tolist()
nodes = [(np.cos(angle), np.sin(angle) + 1) for angle in angles]  # Shift nodes up by 1

# Create the graph
G = nx.Graph()

# Custom function to draw more curved edges within the circle with thicker lines
def draw_more_curved_edges_within_circle_thicker(G, pos, ax, radius=0.6, linewidth=140):
    for (u, v) in G.edges():
        rad = radius if np.random.rand() > 0.5 else -radius  # Randomize the direction of the curve
        random_color = (random.random(), random.random(), random.random())
        ax.annotate(
            '',
            xy=pos[v], xycoords='data',
            xytext=pos[u], textcoords='data',
            arrowprops=dict(
                arrowstyle='-', 
                color=random_color,
                shrinkA=5,
                shrinkB=5,
                connectionstyle=f"arc3,rad={rad}",
                lw=linewidth
            )
        )

# Add nodes to the graph
for i, (x, y) in enumerate(nodes):
    G.add_node(i, pos=(x, y))

# Add edges with 25% probability
for i in range(num_nodes):
    for j in range(i + 1, num_nodes):
        if np.random.rand() < 0.25:
            G.add_edge(i, j)

# Get positions for all nodes
pos = nx.get_node_attributes(G, 'pos')

# Draw the graph with more curved and thicker edges within the circle
fig, ax = plt.subplots(figsize=(200, 200))  # Adjusted size for better visibility
nx.draw_networkx_labels(G, pos, ax=ax)

# Draw the custom more curved and thicker edges within the circle
draw_more_curved_edges_within_circle_thicker(G, pos, ax)

nx.draw_networkx_nodes(G, pos, node_size=150000, node_color="black", ax=ax)

# Set limits to keep the curves within the circle
circle_radius = 1.4
plt.xlim(-circle_radius, circle_radius)
plt.ylim(-0.2, 2.2)  # Adjusted y-limits to show the top half properly
plt.gca().set_aspect('equal', adjustable='box')

plt.axis('off')
plt.show()