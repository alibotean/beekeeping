from seasonal_bee_simulator import SeasonalBeeSimulator
from maramures_calendar import BAIA_MARE_CALENDAR
from simulation_reporter import SimulationReporter
from simulation_plotter import SimulationPlotter

sim = SeasonalBeeSimulator(
    calendar=BAIA_MARE_CALENDAR,
    start_date=(3, 1),  # March 1st
    base_egg_laying_rate=1100,
    base_attrition_rate=600,  # Important: Use 600 for realistic dynamics
    total_frames=8,
    initial_brood_frames=5
)

results = sim.run_simulation(num_days=270).to_dataframes()  # March - November

reporter = SimulationReporter(results)
reporter.print_summary()

plotter = SimulationPlotter(results)
plotter.plot_all()
