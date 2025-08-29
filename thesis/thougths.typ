#show link: underline

= *Thesis title*

== Motivation:
- Agent based modeling is closer tied to the real world than common economic equations.
- With today's extensive compute power technology, it computationally viable to simulate a large enough amounts of agents with aequatetly complex interactions to derive macroeconomic results from microeconomic theory and experimentation.

== Background:
#link("https://www.sciencedirect.com/science/article/pii/S0014292122001891")[https://www.sciencedirect.com/science/article/pii/S0014292122001891] 
- Defineing some external enviroment is nessecary for a realistic ABM because any system unless all variables are completly unaffected by an external enviroment, cannot be represented and simulated in its entirity unless the whole universe is simulated.

== Method:
+ Define agents from common sence(as of now initially)
+ Define interacions from common sence(as of now initially)
+ Define external enviroment form the OECD database or similar
+ Define initial conditions from the OECD database or similar
+ Simulate many times (monte carlo) with random variables being reset each time
+ Compare with AR(0) and other status quo economic predictors 
+ Reajust agent paremeters, agent interactions and enviroment from result of comparison using reinforcement learning

== Two types of interations; monetary and relational
At the root of most economic desitions both at an individual and a collective scale, the agents relation to eachother plays an important role. (One does not buy a car purely from an objective performance vs need vs cost basis. A persons history, impression and overal feeling (humør) also plays a large part in decitionmaking). These relational interactions interact affect monetary ones and vice versa(monetary affects relational). Therefore both of these will be concidered when defining and simulating agents. 

In this thesis relational variables will be marked with an R at the end to separete them from monetary.
 
Laws as well? idk TBD
  
Some relations have many layers. These will therefore be represented as vectors and symbolised with a "V" at the end.

Agents definitnions:
- Government
  - Inputs: taxes, internalSentimentRV, internationalsentimentRV
  - Inner structure: peopleTBD
  - Outputs: laws and regulationsL, subsedies, tax returns, rethoricR
- Central bank
  - Inputs
  - Inner structure
  - Outputs
- Bank
  - Inputs
  - Inner structure
  - Outputs
- Company
  - Inputs
  - Inner structure
  - Outputs
- Household
  - Inputs
  - Inner structure
  - Outputs

