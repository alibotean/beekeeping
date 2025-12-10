from bee_population import BeeHiveSimulator
from simulation_reporter import SimulationReporter
from simulation_plotter import SimulationPlotter

sim = BeeHiveSimulator(
    total_frames=10,
    initial_brood_frames=7,
    attrition_rate=300,
    egg_laying_rate=1100
)

# Queen is lost on day 3
results = sim.run_simulation(
    num_days=80,
    frames_to_add={1: 2, 10: 1, 20: 1},
    queen_loss_day=3
).to_dataframes()

reporter = SimulationReporter(results)
reporter.print_summary()

plotter = SimulationPlotter(results)
plotter.plot_all()
