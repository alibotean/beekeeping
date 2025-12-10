from bee_population import BeeHiveSimulator
from simulation_reporter import SimulationReporter
from simulation_plotter import SimulationPlotter

sim = BeeHiveSimulator(
    total_frames=10,
    initial_brood_frames=8,
    attrition_rate=800,     # Higher losses as foragers age
    egg_laying_rate=1000,     # Queen slowing down
)
results = sim.run_simulation(num_days=60).to_dataframes()

reporter = SimulationReporter(results)
reporter.print_summary()

plotter = SimulationPlotter(results)
plotter.plot_all()
