sim = BeeHiveSimulator(
    total_frames=10,
    initial_brood_frames=4,  # Starting small in spring
    attrition_rate=800,      # Lower mortality in good weather
    egg_laying_rate=1500,    # Strong queen in peak season
)
sim.run_simulation(num_days=90, frames_to_add={7: 2, 14: 2, 28: 2})
sim.plot_results()
