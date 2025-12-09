from bee_population import *

sim = BeeHiveSimulator(
    total_frames=12,         # Extra frames to give more space
    initial_brood_frames=7,
    egg_laying_rate=1400,    # Very productive queen
)
sim.run_simulation(num_days=45, frames_to_add={3: 1, 10: 2, 20: 1})
sim.plot_results()
