sim = BeeHiveSimulator(
    total_frames=10,
    initial_brood_frames=8,
    attrition_rate=1200,     # Higher losses as foragers age
    egg_laying_rate=600,     # Queen slowing down
)
sim.run_simulation(num_days=60, frames_to_add={})  # No expansion
sim.plot_results()
