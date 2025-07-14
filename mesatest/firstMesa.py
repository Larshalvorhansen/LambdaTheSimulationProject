from mesa import Agent


class WalkerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        possible_steps = self.model.grid.get_nerighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)


from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation


class WalkerModel(Model):
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)

        for i in range(self.num_agents):
            agent = WalkerAgent(i, self)
            self.schedule.add(agent)
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(agent, (x, y))

    def step(self):
        self.schedule.step()


if __name__ == "__main__":
    model = WalkerModel(N=5, width=5, height=5)
    for i in range(10):
        model.step()
        print(f"Step {i}")
        for agent in model.schedule.agents:
            print(f" Agent {agent.unique_id} at {agent.pos}")
