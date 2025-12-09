from bee_population import *

sim = BeeHiveSimulator(
    total_frames=10,
    initial_brood_frames=8,
    attrition_rate=800,     # Higher losses as foragers age
    egg_laying_rate=1000,     # Queen slowing down
)
sim.run_simulation(num_days=60)
sim.plot_results()
