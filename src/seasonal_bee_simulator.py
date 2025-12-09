"""
Seasonal Bee Population Simulator for Maramures

This module extends the base BeeHiveSimulator to incorporate seasonal calendar effects,
modulating queen egg-laying rates and bee attrition based on nectar and pollen
availability throughout the year.

The simulator uses the Maramures honey flow calendar to dynamically adjust colony
behavior based on the natural seasonal cycle of forage availability.
"""

import numpy as np
import matplotlib.pyplot as plt
from bee_population import BeeHiveSimulator
from maramures_calendar import MaramuresCalendar


class SeasonalBeeSimulator(BeeHiveSimulator):
    """
    Extended bee colony simulator with calendar-driven seasonal modulation.

    This simulator inherits all functionality from BeeHiveSimulator while adding
    dynamic rate modulation based on seasonal nectar and pollen flows. The queen's
    egg-laying rate and colony attrition rate are adjusted daily according to the
    active flow periods defined in the calendar.

    Key differences from base simulator:
    - Accepts a calendar parameter defining seasonal flows
    - Takes a start_date to align simulation with calendar
    - Modulates rates dynamically based on day of year
    - Tracks calendar dates and active flows in history
    - Enhanced plotting with seasonal flow visualization

    Example:
        from seasonal_bee_simulator import SeasonalBeeSimulator
        from maramures_calendar import BAIA_MARE_CALENDAR

        sim = SeasonalBeeSimulator(
            calendar=BAIA_MARE_CALENDAR,
            start_date=(3, 1),  # March 1st
            base_egg_laying_rate=1100,
            base_attrition_rate=300,
            total_frames=10,
            initial_brood_frames=6
        )

        sim.run_simulation(num_days=270)
        sim.plot_results()
    """

    def __init__(self,
                 calendar: MaramuresCalendar,
                 start_date: tuple = (3, 1),
                 base_egg_laying_rate: int = 1100,
                 base_attrition_rate: int = 300,
                 **kwargs):
        """
        Initialize the seasonal bee simulator.

        Args:
            calendar: MaramuresCalendar instance defining seasonal flows
            start_date: Tuple of (month, day) for simulation start date.
                       Default is March 1st (3, 1)
            base_egg_laying_rate: Baseline eggs laid per day (before modulation).
                                 Default is 1100 eggs/day
            base_attrition_rate: Baseline adult bees dying per day (before modulation).
                                Default is 300 bees/day
            **kwargs: Additional parameters passed to BeeHiveSimulator
                     (total_frames, initial_brood_frames, etc.)
        """
        # Store calendar and base rates
        self.calendar = calendar
        self.start_date = start_date
        self.base_egg_laying_rate = base_egg_laying_rate
        self.base_attrition_rate = base_attrition_rate

        # Calculate starting day of year
        self.current_day_of_year = self._date_to_day_of_year(start_date)

        # Initialize parent class with base rates
        # Note: These will be temporarily overridden each day in simulate_day
        super().__init__(
            egg_laying_rate=base_egg_laying_rate,
            attrition_rate=base_attrition_rate,
            **kwargs
        )

        # Add calendar-specific history tracking
        self.history['calendar_date'] = []
        self.history['active_flows'] = []
        self.history['effective_egg_rate'] = []
        self.history['effective_attrition'] = []
        self.history['nectar_availability'] = []
        self.history['pollen_availability'] = []

    def _date_to_day_of_year(self, date: tuple) -> int:
        """
        Convert (month, day) tuple to day of year (1-365).

        Args:
            date: Tuple of (month, day) where month is 1-12 and day is 1-31

        Returns:
            Day of year as integer (1-365)
        """
        month, day = date
        # Days before each month in non-leap year
        days_before_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        return days_before_month[month - 1] + day

    def simulate_day(self, day: int):
        """
        Simulate one day with calendar-driven rate modulation.

        This method overrides the parent's simulate_day to apply seasonal
        modulation to egg-laying and attrition rates based on the current
        calendar date.

        Args:
            day: Simulation day number (0-indexed from start of simulation)
        """
        # Get calendar factors for current day of year
        factors = self.calendar.get_daily_factors(self.current_day_of_year)

        # Calculate effective rates by applying calendar modifiers
        effective_egg_rate = int(self.base_egg_laying_rate * factors['egg_rate_modifier'])
        effective_attrition = int(self.base_attrition_rate * factors['attrition_modifier'])

        # Ensure rates don't go below minimums
        effective_egg_rate = max(0, effective_egg_rate)
        effective_attrition = max(0, effective_attrition)

        # Store original rates
        original_egg = self.egg_laying_rate
        original_attrition = self.attrition_rate

        # Temporarily set modulated rates for this day
        self.egg_laying_rate = effective_egg_rate
        self.attrition_rate = effective_attrition

        # Call parent's simulate_day with the modulated rates
        super().simulate_day(day)

        # Restore original base rates
        self.egg_laying_rate = original_egg
        self.attrition_rate = original_attrition

        # Track calendar-specific data
        active_flows = self.calendar.get_active_flows(self.current_day_of_year)
        date_string = self.calendar.day_of_year_to_date_string(self.current_day_of_year)

        self.history['calendar_date'].append(date_string)
        self.history['active_flows'].append([f.name for f in active_flows])
        self.history['effective_egg_rate'].append(effective_egg_rate)
        self.history['effective_attrition'].append(effective_attrition)
        self.history['nectar_availability'].append(factors['nectar_availability'])
        self.history['pollen_availability'].append(factors['pollen_availability'])

        # Increment day of year (wrap at 365)
        self.current_day_of_year = (self.current_day_of_year % 365) + 1

    def run_simulation(self, num_days: int, frames_to_add: dict = None, queen_loss_day: int = None):
        """
        Run the simulation with seasonal calendar integration.

        This overrides the parent's run_simulation to provide calendar-aware
        status messages.

        Args:
            num_days: Number of days to simulate
            frames_to_add: Dict mapping day number to number of frames to add
            queen_loss_day: Day on which the queen is lost (None = no queen loss)
        """
        if frames_to_add is None:
            frames_to_add = {}

        start_date_str = self.calendar.day_of_year_to_date_string(
            self._date_to_day_of_year(self.start_date)
        )

        print(f"\n=== Seasonal Bee Population Simulation ===")
        print(f"Location: {self.calendar.location_name}")
        print(f"Start date: {start_date_str} (Day of year: {self._date_to_day_of_year(self.start_date)})")
        print(f"Simulation duration: {num_days} days")
        print(f"Initial adult bees: {self.adult_bees:,}")
        print(f"Initial brood frames: {self.brood_frames}")
        print(f"Base egg laying rate: {self.base_egg_laying_rate} eggs/day (modulated by calendar)")
        print(f"Base attrition rate: {self.base_attrition_rate} bees/day (modulated by calendar)")
        if queen_loss_day is not None:
            print(f"Queen loss scheduled for day: {queen_loss_day}")
        print()

        for day in range(num_days):
            # Check if we should add frames on this day
            if day in frames_to_add:
                self.add_frames(frames_to_add[day])

            # Check if queen is lost on this day
            if queen_loss_day is not None and day == queen_loss_day:
                self.lose_queen(day)

            # Simulate the day
            self.simulate_day(day)

            # Print status every 30 days (monthly update)
            if day % 30 == 0:
                eggs, larvae, pupae = self.get_brood_by_stage()
                occupancy = self.get_brood_occupancy_percentage()
                date_str = self.history['calendar_date'][-1]
                active_flows = self.history['active_flows'][-1]

                print(f"Day {day:3d} ({date_str}): Adult bees: {self.adult_bees:6,}, "
                      f"Brood: {self.get_current_brood_count():6,}, "
                      f"Occupancy: {occupancy:5.1f}%")
                if active_flows:
                    print(f"           Active flows: {', '.join(active_flows[:3])}")

        print(f"\n=== Simulation Complete ===")
        print(f"Final adult population: {self.adult_bees:,}")
        print(f"Final brood count: {self.get_current_brood_count():,}")
        print(f"Final date: {self.history['calendar_date'][-1]}")

    def plot_results(self):
        """
        Create enhanced visualizations with seasonal flow overlays.

        This extends the parent's plot_results to include:
        - Calendar dates on x-axis
        - Vertical bands showing major flow periods
        - Additional panel showing effective rates over time
        - Seasonal context annotations
        """
        fig, axes = plt.subplots(3, 2, figsize=(16, 15))
        fig.suptitle(f'Seasonal Bee Colony Dynamics - {self.calendar.location_name}',
                     fontsize=16, fontweight='bold')

        days = self.history['day']
        dates = self.history['calendar_date']

        # Determine x-axis tick positions (show every 30 days)
        tick_indices = list(range(0, len(days), 30))
        if len(days) - 1 not in tick_indices:
            tick_indices.append(len(days) - 1)

        # Plot 1: Adult bee population over time
        ax1 = axes[0, 0]
        ax1.plot(days, self.history['adult_bees'], 'b-', linewidth=2)
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Adult Bees')
        ax1.set_title('Adult Bee Population')
        ax1.grid(True, alpha=0.3)
        ax1.fill_between(days, self.history['adult_bees'], alpha=0.3)
        ax1.set_xticks([days[i] for i in tick_indices])
        ax1.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')

        # Plot 2: Brood population over time
        ax2 = axes[0, 1]
        ax2.plot(days, self.history['total_brood'], 'g-', linewidth=2)
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Developing Brood')
        ax2.set_title('Total Brood (Eggs, Larvae, Pupae)')
        ax2.grid(True, alpha=0.3)
        ax2.fill_between(days, self.history['total_brood'], alpha=0.3, color='green')
        ax2.set_xticks([days[i] for i in tick_indices])
        ax2.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')

        # Plot 3: Effective egg laying and attrition rates
        ax3 = axes[1, 0]
        ax3.plot(days, self.history['effective_egg_rate'], 'orange',
                linewidth=2, label='Egg Laying Rate')
        ax3.plot(days, self.history['effective_attrition'], 'red',
                linewidth=2, label='Attrition Rate')
        ax3.set_xlabel('Days')
        ax3.set_ylabel('Bees per Day')
        ax3.set_title('Calendar-Modulated Rates')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xticks([days[i] for i in tick_indices])
        ax3.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')

        # Plot 4: Net daily change (emerged - died)
        ax4 = axes[1, 1]
        net_change = [emerged - died for emerged, died in
                     zip(self.history['bees_emerged'], self.history['bees_died'])]
        colors = ['green' if x >= 0 else 'red' for x in net_change]
        ax4.bar(days, net_change, color=colors, alpha=0.6)
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Net Change in Adult Bees')
        ax4.set_title('Daily Population Change (Emerged - Died)')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_xticks([days[i] for i in tick_indices])
        ax4.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')

        # Plot 5: Nectar and pollen availability
        ax5 = axes[2, 0]
        ax5.plot(days, self.history['nectar_availability'], 'gold',
                linewidth=2, label='Nectar', alpha=0.8)
        ax5.plot(days, self.history['pollen_availability'], 'brown',
                linewidth=2, label='Pollen', alpha=0.8)
        ax5.set_xlabel('Days')
        ax5.set_ylabel('Availability (0-1)')
        ax5.set_title('Seasonal Forage Availability')
        ax5.set_ylim(-0.05, 1.05)
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_xticks([days[i] for i in tick_indices])
        ax5.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')

        # Plot 6: Brood cell occupancy percentage with detailed breakdown
        ax6 = axes[2, 1]

        # Main line and fill
        line, = ax6.plot(days, self.history['brood_occupancy_pct'], 'r-', linewidth=2, label='Occupancy')
        ax6.fill_between(days, self.history['brood_occupancy_pct'], alpha=0.3, color='red')

        # Add scatter points every 5 days for tooltip targets
        sample_indices = list(range(0, len(days), 5))
        scatter = ax6.scatter([days[i] for i in sample_indices],
                             [self.history['brood_occupancy_pct'][i] for i in sample_indices],
                             c='darkred', s=30, alpha=0.6, zorder=5)

        # Reference lines
        ax6.axhline(y=80, color='orange', linestyle='--', linewidth=1, label='80% (High)')
        ax6.axhline(y=50, color='yellow', linestyle='--', linewidth=1, label='50% (Medium)')

        ax6.set_xlabel('Days')
        ax6.set_ylabel('Occupancy (%)')
        ax6.set_title('Brood Cell Occupancy (hover over points for details)')
        ax6.set_ylim(0, 100)
        ax6.legend(loc='upper left')
        ax6.grid(True, alpha=0.3)
        ax6.set_xticks([days[i] for i in tick_indices])
        ax6.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')

        # Create annotation for tooltip
        annot = ax6.annotate("", xy=(0, 0), xytext=(15, 15),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.9),
                            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
                            fontsize=8, visible=False, zorder=10)

        # Hover event handler
        def hover(event):
            if event.inaxes == ax6:
                # Check if mouse is near any scatter point
                cont, ind = scatter.contains(event)
                if cont:
                    # Get the index of the closest point
                    idx = sample_indices[ind["ind"][0]]

                    # Get data for this day
                    date = dates[idx]
                    eggs = self.history['eggs'][idx]
                    larvae = self.history['larvae'][idx]
                    pupae = self.history['pupae'][idx]
                    total = self.history['total_brood'][idx]
                    occupancy = self.history['brood_occupancy_pct'][idx]
                    capacity = self.get_max_brood_capacity()

                    # Calculate percentages of total brood
                    egg_pct = (eggs / total * 100) if total > 0 else 0
                    larvae_pct = (larvae / total * 100) if total > 0 else 0
                    pupae_pct = (pupae / total * 100) if total > 0 else 0

                    # Format tooltip text
                    text = f"{date} (Day {days[idx]})\n"
                    text += f"Occupancy: {occupancy:.1f}%\n"
                    text += f"Total: {total:,} / {capacity:,} cells\n"
                    text += f"─────────────────\n"
                    text += f"Eggs:   {eggs:5,} ({egg_pct:4.1f}%)\n"
                    text += f"Larvae: {larvae:5,} ({larvae_pct:4.1f}%)\n"
                    text += f"Pupae:  {pupae:5,} ({pupae_pct:4.1f}%)"

                    annot.set_text(text)
                    annot.xy = (days[idx], self.history['brood_occupancy_pct'][idx])
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if annot.get_visible():
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        # Connect the hover event
        fig.canvas.mpl_connect("motion_notify_event", hover)

        plt.tight_layout()
        plt.show()

    def print_seasonal_summary(self):
        """
        Print a summary of the simulation with seasonal highlights.

        Useful for understanding which flow periods had the most impact
        on colony dynamics.
        """
        print("\n=== Seasonal Flow Summary ===")

        # Find all unique flow names that were active during simulation
        all_flows = set()
        for flow_list in self.history['active_flows']:
            all_flows.update(flow_list)

        print(f"Total unique flows encountered: {len(all_flows)}")
        print(f"Flows: {', '.join(sorted(all_flows))}")

        # Find peak population
        max_adults = max(self.history['adult_bees'])
        max_adults_day = self.history['adult_bees'].index(max_adults)
        max_adults_date = self.history['calendar_date'][max_adults_day]

        print(f"\nPeak adult population: {max_adults:,} bees on day {max_adults_day} ({max_adults_date})")

        # Find max brood
        max_brood = max(self.history['total_brood'])
        max_brood_day = self.history['total_brood'].index(max_brood)
        max_brood_date = self.history['calendar_date'][max_brood_day]

        print(f"Peak brood: {max_brood:,} cells on day {max_brood_day} ({max_brood_date})")

        # Find max and min egg laying rates
        max_egg_rate = max(self.history['effective_egg_rate'])
        min_egg_rate = min(self.history['effective_egg_rate'])

        print(f"\nEgg laying rate range: {min_egg_rate} - {max_egg_rate} eggs/day")
        print(f"Base rate: {self.base_egg_laying_rate} eggs/day")


if __name__ == "__main__":
    # Example usage
    from maramures_calendar import BAIA_MARE_CALENDAR

    print("Creating seasonal bee simulator for Baia Mare...")

    # Create simulator starting March 1st
    sim = SeasonalBeeSimulator(
        calendar=BAIA_MARE_CALENDAR,
        start_date=(3, 1),          # March 1st - beginning of spring
        base_egg_laying_rate=1100,  # Average queen performance
        base_attrition_rate=600,    # Base mortality (realistic for large colonies)
        total_frames=10,
        initial_brood_frames=6
    )

    # Run simulation for 270 days (March 1 through November 26)
    sim.run_simulation(num_days=270)

    # Print seasonal summary
    sim.print_seasonal_summary()

    # Plot results
    sim.plot_results()
