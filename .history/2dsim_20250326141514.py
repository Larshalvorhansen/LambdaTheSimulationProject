import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Constants
WORLD_SIZE = 100
NUM_CUSTOMERS = 20
NUM_COMPANIES = 5
NUM_BANKS = 2
RESOURCE_GROWTH_RATE = 0.01
INITIAL_RESOURCES = 10000
TICKS = 100

class Earth:
    def __init__(self):
        self.resources = INITIAL_RESOURCES

    def grow(self):
        self.resources += self.resources * RESOURCE_GROWTH_RATE

    def extract(self, amount):
        if amount > self.resources:
            amount = self.resources
        self.resources -= amount
        return amount

class State:
    def __init__(self):
        self.interest_rate = 0.05

    def regulate(self, economy_health):
        if economy_health < 0.5:
            self.interest_rate = max(0.01, self.interest_rate - 0.01)
        else:
            self.interest_rate += 0.01

class Bank:
    def __init__(self, state):
        self.state = state
        self.total_money = 100000

    def lend(self, company, amount):
        interest = amount * self.state.interest_rate
        company.receive_loan(amount)
        self.total_money -= amount
        return interest

class Company:
    def __init__(self, x, y, earth):
        self.x = x
        self.y = y
        self.money = 1000
        self.resources = 0
        self.earth = earth
        self.loan = 0

    def produce(self):
        used = self.earth.extract(10)
        self.resources += used

    def sell_to(self, customer):
        if self.resources > 0 and customer.money >= 5:
            customer.money -= 5
            self.money += 5
            self.resources -= 1

    def pay_wage(self, customer):
        customer.money += 2
        self.money -= 2

    def receive_loan(self, amount):
        self.money += amount
        self.loan += amount

class Customer:
    def __init__(self):
        self.x = random.randint(0, WORLD_SIZE)
        self.y = random.randint(0, WORLD_SIZE)
        self.money = 100

    def move(self):
        self.x = (self.x + random.choice([-1, 0, 1])) % WORLD_SIZE
        self.y = (self.y + random.choice([-1, 0, 1])) % WORLD_SIZE

    def find_nearby_company(self, companies):
        for company in companies:
            if abs(company.x - self.x) <= 2 and abs(company.y - self.y) <= 2:
                return company
        return None

# Setup
earth = Earth()
state = State()
banks = [Bank(state) for _ in range(NUM_BANKS)]
companies = [Company(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), earth) for _ in range(NUM_COMPANIES)]
customers = [Customer() for _ in range(NUM_CUSTOMERS)]

# Visualization setup
fig, ax = plt.subplots()
sc_customers = ax.scatter([], [], c='blue', label='Customers')
sc_companies = ax.scatter([], [], c='green', label='Companies')
text_info = ax.text(0.02, 0.95, '', transform=ax.transAxes)

def init():
    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    ax.legend(loc='upper right')
    return sc_customers, sc_companies, text_info

def update(frame):
    # Earth grows
    earth.grow()

    # Companies produce
    for company in companies:
        company.produce()

    # Customers move and interact
    for customer in customers:
        customer.move()
        nearby_company = customer.find_nearby_company(companies)
        if nearby_company:
            nearby_company.pay_wage(customer)
            nearby_company.sell_to(customer)

    # Banks lend to companies
    for bank in banks:
        for company in companies:
            if company.money < 200:
                bank.lend(company, 500)

    # State regulates interest rate
    avg_company_money = sum(c.money for c in companies) / NUM_COMPANIES
    economy_health = avg_company_money / 1000
    state.regulate(economy_health)

    # Update plot
    customer_coords = [(c.x, c.y) for c in customers]
    company_coords = [(c.x, c.y) for c in companies]

    sc_customers.set_offsets(customer_coords)
    sc_companies.set_offsets(company_coords)
    text_info.set_text(f"Tick {frame}\nResources: {earth.resources:.0f}\nInterest: {state.interest_rate:.2f}")

    return sc_customers, sc_companies, text_info

ani = animation.FuncAnimation(fig, update, frames=TICKS, init_func=init, blit=True, repeat=False)
plt.close()
ani
