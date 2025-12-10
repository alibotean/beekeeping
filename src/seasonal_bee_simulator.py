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

        # Honey stores tracking
        self.honey_stores = 15.0  # Start with 15kg winter stores
        self.history['honey_stores'] = []
        self.history['daily_honey_production'] = []
        self.history['daily_honey_consumption'] = []
        self.history['net_honey_change'] = []
        self.history['supering_recommendations'] = []

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

    def _calculate_honey_production(self, nectar_availability: float) -> float:
        """
        Calculate daily honey production based on nectar availability and forager population.

        Assumptions:
        - ~25-35% of adult bees are foragers (varies by age distribution)
        - Effective collection rate accounts for: multiple trips, partial loads,
          unsuccessful trips, weather interruptions, and foraging efficiency
        - Peak flow (nectar=1.0): Strong colony brings ~4-5 kg nectar/day → ~1.6-2.0 kg honey/day
        - Nectar → honey conversion is ~2.5:1 (honey is concentrated nectar)
        - Realistic surplus: 30-50 kg per hive per season

        Args:
            nectar_availability: 0.0-1.0 indicating nectar flow strength

        Returns:
            Daily honey production in kg
        """
        # Estimate forager population (25-35% of adults, more during flows)
        forager_percentage = 0.25 + (nectar_availability * 0.10)  # 25-35%
        foragers = self.adult_bees * forager_percentage

        # Effective nectar collection per forager per day (accounts for all factors)
        # Peak conditions (nectar=1.0): ~150mg effective collection per forager
        # This is the NET result of: trips × load × success_rate × weather × efficiency
        effective_nectar_per_forager = 0.00015 * nectar_availability  # kg

        # Total nectar collected
        total_nectar = foragers * effective_nectar_per_forager

        # Convert to honey (2.5:1 ratio)
        honey_produced = total_nectar / 2.5

        return honey_produced

    def _calculate_honey_consumption(self) -> float:
        """
        Calculate daily honey consumption for colony maintenance and brood rearing.

        Assumptions:
        - Adult bee: ~10mg honey/day = 0.00001 kg
        - Brood cell: ~20mg honey equivalent over development = ~1mg/day = 0.000001 kg
        - More consumption during cold weather (cluster heating)

        Returns:
            Daily honey consumption in kg
        """
        # Adult bee consumption (10mg/bee/day)
        adult_consumption = self.adult_bees * 0.00001

        # Brood consumption (nurse bees feeding larvae)
        # Effective consumption ~1mg/cell/day
        brood_consumption = self.get_current_brood_count() * 0.000001

        total_consumption = adult_consumption + brood_consumption

        return total_consumption

    def _should_super(self, factors: dict, day: int) -> tuple:
        """
        Determine if this is a good time to add honey supers.

        Criteria for supering:
        1. Brood nest occupancy >= 70% (colony is strong)
        2. Nectar availability >= 0.6 (good flow active or imminent)
        3. Honey stores >= 8kg (colony has sufficient reserves)
        4. Not in winter dormancy (Nov-Feb)

        Returns:
            Tuple of (should_super: bool, reason: str)
        """
        occupancy = self.get_brood_occupancy_percentage()
        nectar = factors['nectar_availability']

        # Check criteria
        if self.current_day_of_year < 60 or self.current_day_of_year > 305:
            # Winter period (Jan-Feb, Nov-Dec)
            return False, ""

        if occupancy >= 70 and nectar >= 0.6 and self.honey_stores >= 8:
            flow_names = ', '.join(factors['active_flow_names'][:2])
            return True, f"SUPER NOW! {flow_names} flow active, {occupancy:.0f}% brood occupancy"

        # Check for upcoming major flows (within 5 days)
        upcoming_strong = False
        for future_day in range(1, 6):
            future_doy = ((self.current_day_of_year + future_day - 1) % 365) + 1
            future_factors = self.calendar.get_daily_factors(future_doy)
            if future_factors['nectar_availability'] >= 0.8:
                upcoming_strong = True
                break

        if occupancy >= 65 and upcoming_strong and self.honey_stores >= 8:
            return True, f"SUPER NOW! Major flow starting in <5 days, {occupancy:.0f}% occupancy"

        return False, ""

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

        # Calculate honey production and consumption
        honey_produced = self._calculate_honey_production(factors['nectar_availability'])
        honey_consumed = self._calculate_honey_consumption()
        net_honey_change = honey_produced - honey_consumed

        # Update honey stores
        self.honey_stores += net_honey_change
        # Don't let stores go negative (colony would starve in reality)
        self.honey_stores = max(0, self.honey_stores)

        # Check if supering is recommended
        should_super, super_reason = self._should_super(factors, day)

        # Track calendar-specific data
        active_flows = self.calendar.get_active_flows(self.current_day_of_year)
        date_string = self.calendar.day_of_year_to_date_string(self.current_day_of_year)

        self.history['calendar_date'].append(date_string)
        self.history['active_flows'].append([f.name for f in active_flows])
        self.history['effective_egg_rate'].append(effective_egg_rate)
        self.history['effective_attrition'].append(effective_attrition)
        self.history['nectar_availability'].append(factors['nectar_availability'])
        self.history['pollen_availability'].append(factors['pollen_availability'])

        # Track honey stores
        self.history['honey_stores'].append(self.honey_stores)
        self.history['daily_honey_production'].append(honey_produced)
        self.history['daily_honey_consumption'].append(honey_consumed)
        self.history['net_honey_change'].append(net_honey_change)
        self.history['supering_recommendations'].append(super_reason if should_super else "")

        # Increment day of year (wrap at 365)
        self.current_day_of_year = (self.current_day_of_year % 365) + 1

    def to_dataframes(self):
        """
        Convert simulation results to structured pandas DataFrames (seasonal extension).

        Extends the base method to include calendar and resource DataFrames.

        Returns:
            Dictionary containing:
            - 'population': DataFrame with adult_bees, brood stages, occupancy
            - 'dynamics': DataFrame with daily changes and rates
            - 'events': DataFrame with discrete events
            - 'calendar': DataFrame with seasonal flow data
            - 'resources': DataFrame with honey tracking
            - 'metadata': Dict with configuration and parameters
        """
        import pandas as pd
        import json

        # Get base DataFrames from parent class
        results = super().to_dataframes()

        # Handle empty simulation
        if not self.history['day']:
            results['calendar'] = pd.DataFrame(columns=['day', 'calendar_date', 'day_of_year', 'active_flows',
                                                        'nectar_availability', 'pollen_availability',
                                                        'egg_rate_modifier', 'attrition_modifier',
                                                        'effective_egg_rate', 'effective_attrition'])
            results['resources'] = pd.DataFrame(columns=['day', 'honey_stores', 'daily_honey_production',
                                                         'daily_honey_consumption', 'net_honey_change',
                                                         'supering_recommendation'])
            # Add calendar info to metadata
            results['metadata']['calendar_info'] = {
                'location_name': getattr(self.calendar, 'name', 'Unknown'),
                'start_date': self.start_date,
                'base_egg_laying_rate': self.base_egg_laying_rate,
                'base_attrition_rate': self.base_attrition_rate
            }
            return results

        # Add calendar DataFrame
        # Reconstruct day_of_year for each day
        start_doy = self._date_to_day_of_year(self.start_date)
        days_of_year = [(start_doy + i - 1) % 365 + 1 for i in range(len(self.history['day']))]

        # Calculate modifiers from effective rates
        egg_rate_modifiers = []
        attrition_modifiers = []
        for eff_egg, eff_attr in zip(self.history['effective_egg_rate'], self.history['effective_attrition']):
            egg_mod = eff_egg / self.base_egg_laying_rate if self.base_egg_laying_rate > 0 else 0
            attr_mod = eff_attr / self.base_attrition_rate if self.base_attrition_rate > 0 else 0
            egg_rate_modifiers.append(egg_mod)
            attrition_modifiers.append(attr_mod)

        results['calendar'] = pd.DataFrame({
            'day': self.history['day'],
            'calendar_date': self.history['calendar_date'],
            'day_of_year': days_of_year,
            'active_flows': [json.dumps(flows) for flows in self.history['active_flows']],
            'nectar_availability': self.history['nectar_availability'],
            'pollen_availability': self.history['pollen_availability'],
            'egg_rate_modifier': egg_rate_modifiers,
            'attrition_modifier': attrition_modifiers,
            'effective_egg_rate': self.history['effective_egg_rate'],
            'effective_attrition': self.history['effective_attrition']
        }).set_index('day')

        # Add resources DataFrame
        results['resources'] = pd.DataFrame({
            'day': self.history['day'],
            'honey_stores': self.history['honey_stores'],
            'daily_honey_production': self.history['daily_honey_production'],
            'daily_honey_consumption': self.history['daily_honey_consumption'],
            'net_honey_change': self.history['net_honey_change'],
            'supering_recommendation': self.history['supering_recommendations']
        }).set_index('day')

        # Add seasonal metadata
        results['metadata']['calendar_info'] = {
            'location_name': getattr(self.calendar, 'name', 'Unknown'),
            'start_date': self.start_date,
            'base_egg_laying_rate': self.base_egg_laying_rate,
            'base_attrition_rate': self.base_attrition_rate
        }

        return results

    def run_simulation(self, num_days: int, frames_to_add: dict = None, queen_loss_day: int = None):
        """
        Run the simulation with seasonal calendar integration.

        Args:
            num_days: Number of days to simulate
            frames_to_add: Dict mapping day number to number of frames to add
            queen_loss_day: Day on which the queen is lost (None = no queen loss)

        Returns:
            self (for method chaining)
        """
        # Call parent's run_simulation which now handles everything silently
        return super().run_simulation(num_days, frames_to_add, queen_loss_day)


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
