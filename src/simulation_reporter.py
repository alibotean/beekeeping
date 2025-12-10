"""
Simulation Reporter - Console output for bee colony simulations.

This module handles all console output for bee simulation results,
supporting both base BeeHiveSimulator and SeasonalBeeSimulator.
"""

import json
import pandas as pd


class SimulationReporter:
    """
    Handles all console output for bee colony simulations.

    Supports both BeeHiveSimulator and SeasonalBeeSimulator results.
    Automatically detects simulator type and provides appropriate output.
    """

    def __init__(self, results: dict):
        """
        Initialize reporter with simulation results.

        Args:
            results: Dictionary returned by simulator.to_dataframes()
        """
        self.results = results
        self.metadata = results['metadata']
        self.population = results['population']
        self.dynamics = results['dynamics']
        self.events = results.get('events')

        # Seasonal-specific data
        self.is_seasonal = 'calendar' in results
        if self.is_seasonal:
            self.calendar = results['calendar']
            self.resources = results['resources']

    def print_summary(self):
        """Print complete simulation summary (main entry point)."""
        self.print_header()
        print()
        self.print_periodic_status(interval=10 if not self.is_seasonal else 30)
        print()
        self.print_events()

        if self.is_seasonal:
            print()
            self.print_supering_alerts()
            print()
            self.print_seasonal_summary()
            print()
            self.print_honey_summary()

        print()
        self.print_footer()

    def print_header(self):
        """Print simulation start header with configuration."""
        if self.is_seasonal:
            calendar_info = self.metadata.get('calendar_info', {})
            start_date = calendar_info.get('start_date', (1, 1))
            start_doy = self._date_to_day_of_year(start_date)
            # Reconstruct date string
            months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month, day = start_date
            start_date_str = f"{months[month]} {day:02d}"

            print(f"=== Seasonal Bee Population Simulation ===")
            print(f"Location: {calendar_info.get('location_name', 'Unknown')}")
            print(f"Start date: {start_date_str} (Day of year: {start_doy})")
            print(f"Simulation duration: {self.metadata['simulation_parameters'].get('num_days', len(self.population))} days")
            print(f"Initial adult bees: {self.metadata['initial_state']['adult_bees']:,}")
            print(f"Initial brood frames: {self.metadata['simulation_config']['initial_brood_frames']}")
            print(f"Base egg laying rate: {calendar_info.get('base_egg_laying_rate', 0)} eggs/day (modulated by calendar)")
            print(f"Base attrition rate: {calendar_info.get('base_attrition_rate', 0)} bees/day (modulated by calendar)")
        else:
            print(f"=== Starting Bee Population Simulation ===")
            print(f"Initial adult bees: {self.metadata['initial_state']['adult_bees']:,}")
            print(f"Initial brood frames: {self.metadata['simulation_config']['initial_brood_frames']}")
            print(f"Egg laying rate: {self.metadata['base_rates']['egg_laying_rate']} eggs/day")
            print(f"Attrition rate: {self.metadata['base_rates']['attrition_rate']} bees/day")

        queen_loss_day = self.metadata['simulation_parameters'].get('queen_loss_day')
        if queen_loss_day is not None:
            print(f"Queen loss scheduled for day: {queen_loss_day}")

    def print_footer(self):
        """Print simulation end summary."""
        final_adults = self.population.iloc[-1]['adult_bees']
        final_brood = self.population.iloc[-1]['total_brood']

        print(f"=== Simulation Complete ===")
        print(f"Final adult population: {final_adults:,}")
        print(f"Final brood count: {int(final_brood):,}")

        if self.is_seasonal:
            final_date = self.calendar.iloc[-1]['calendar_date']
            print(f"Final date: {final_date}")

    def print_periodic_status(self, interval: int = 10):
        """Print status at regular intervals during simulation."""
        for idx in range(0, len(self.population), interval):
            row = self.population.iloc[idx]
            day = row.name  # day is the index

            if self.is_seasonal:
                cal_row = self.calendar.iloc[idx]
                res_row = self.resources.iloc[idx]

                active_flows = json.loads(cal_row['active_flows'])
                flows_str = ', '.join(active_flows[:3]) if active_flows else 'None'

                print(f"Day {day:3d} ({cal_row['calendar_date']}): "
                      f"Adult bees: {int(row['adult_bees']):6,}, "
                      f"Brood: {int(row['total_brood']):6,}, "
                      f"Occupancy: {row['brood_occupancy_pct']:5.1f}%, "
                      f"Honey: {res_row['honey_stores']:5.1f} kg")
                if active_flows:
                    print(f"           Active flows: {flows_str}")
            else:
                print(f"Day {day:3d}: Adult bees: {int(row['adult_bees']):6,}, "
                      f"Brood: {int(row['total_brood']):6,} "
                      f"(Eggs: {int(row['eggs']):5,}, Larvae: {int(row['larvae']):5,}, "
                      f"Pupae: {int(row['pupae']):5,}), "
                      f"Occupancy: {row['brood_occupancy_pct']:5.1f}%")

    def print_events(self):
        """Print discrete events that occurred during simulation."""
        if self.events is None or len(self.events) == 0:
            return

        print("=== Events ===")
        for _, event in self.events.iterrows():
            print(f"  Day {event['day']}: {event['description']}")

    def print_supering_alerts(self):
        """Print supering recommendations (seasonal only)."""
        if not self.is_seasonal:
            return

        # Filter days with recommendations
        super_recs = self.resources[self.resources['supering_recommendation'] != '']

        if len(super_recs) == 0:
            print("No supering recommendations during this simulation period.")
            return

        print("=== Supering Recommendations ===")
        for idx in super_recs.index:
            row = super_recs.loc[idx]
            cal_date = self.calendar.loc[idx, 'calendar_date']
            print(f"\n  🍯 Day {idx} ({cal_date}): {row['supering_recommendation']}")
            print(f"     Honey stores: {row['honey_stores']:.1f} kg")

    def print_seasonal_summary(self):
        """Print seasonal flow summary (seasonal only)."""
        if not self.is_seasonal:
            return

        print("=== Seasonal Flow Summary ===")

        # Extract unique flows
        all_flows = []
        for flows_json in self.calendar['active_flows']:
            flows = json.loads(flows_json)
            all_flows.extend(flows)
        unique_flows = sorted(set(all_flows))

        print(f"Total unique flows encountered: {len(unique_flows)}")
        print(f"Flows: {', '.join(unique_flows)}")
        print()

        # Find peak values
        peak_adults_idx = self.population['adult_bees'].idxmax()
        peak_adults = self.population.loc[peak_adults_idx, 'adult_bees']
        peak_adults_date = self.calendar.loc[peak_adults_idx, 'calendar_date']

        peak_brood_idx = self.population['total_brood'].idxmax()
        peak_brood = self.population.loc[peak_brood_idx, 'total_brood']

        print(f"Peak adult population: {int(peak_adults):,} bees on day {peak_adults_idx} ({peak_adults_date})")
        print(f"Peak brood: {int(peak_brood):,} cells on day {peak_brood_idx}")
        print()

        # Egg laying rate range
        min_egg = self.calendar['effective_egg_rate'].min()
        max_egg = self.calendar['effective_egg_rate'].max()
        base_egg = self.metadata['calendar_info'].get('base_egg_laying_rate', 0)

        print(f"Egg laying rate range: {int(min_egg)} - {int(max_egg)} eggs/day")
        print(f"Base rate: {base_egg} eggs/day")

    def print_honey_summary(self):
        """Print honey production summary (seasonal only)."""
        if not self.is_seasonal:
            return

        print("=== Honey Production Summary ===")

        total_produced = self.resources['daily_honey_production'].sum()
        total_consumed = self.resources['daily_honey_consumption'].sum()
        net_gain = total_produced - total_consumed
        max_stores = self.resources['honey_stores'].max()
        final_stores = self.resources['honey_stores'].iloc[-1]

        print(f"Total honey produced: {total_produced:.1f} kg")
        print(f"Total honey consumed: {total_consumed:.1f} kg")
        print(f"Net honey gain: {net_gain:.1f} kg")
        print(f"Peak honey stores: {max_stores:.1f} kg")
        print(f"Final honey stores: {final_stores:.1f} kg")

        # Count supering recommendations
        super_count = sum(1 for rec in self.resources['supering_recommendation'] if rec)
        if super_count > 0:
            print(f"\n🍯 Supering recommended {super_count} times during simulation")
            print(f"Review the simulation output above for specific dates")

    def _date_to_day_of_year(self, date: tuple) -> int:
        """Convert (month, day) to day of year (1-365)."""
        month, day = date
        days_before_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        return days_before_month[month - 1] + day
