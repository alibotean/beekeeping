"""
Weather Integration Example

Demonstrates how to integrate WeatherModel with SeasonalBeeSimulator.

The integration follows this hierarchy of modifiers:
1. Base rates (egg_laying_rate, attrition_rate)
2. Calendar modifiers (from honey flows)
3. Weather modifiers (temperature, rain, sunlight)

Final effective rate = Base × Calendar_Modifier × Weather_Modifier

Example:
- Base egg laying: 1100 eggs/day
- Calendar modifier during Acacia: 1.4× (good flow)
- Weather modifier on rainy day: 0.5× (reduced brood rearing)
- Final rate: 1100 × 1.4 × 0.5 = 770 eggs/day
"""

from seasonal_bee_simulator import SeasonalBeeSimulator
from maramures_calendar import BAIA_MARE_CALENDAR
from weather_model import create_baia_mare_weather
from simulation_reporter import SimulationReporter
from simulation_plotter import SimulationPlotter
import matplotlib.pyplot as plt
import pandas as pd


def scenario_weather_impact_comparison():
    """
    Compare bee colony dynamics with and without weather effects.

    This demonstrates the realistic impact of weather on colony development.
    """
    print("\n" + "=" * 80)
    print("SCENARIO: Weather Impact on Colony Development")
    print("=" * 80)

    # Generate weather data
    print("\nGenerating weather data for Baia Mare (March 1 - November 26)...")
    weather_model = create_baia_mare_weather(start_date=(3, 1), seed=42)
    weather_results = weather_model.to_dataframes(num_days=270)
    weather_df = weather_results['weather']

    print(f"Weather generated: {len(weather_df)} days")
    print(f"Rainy days: {weather_df['is_rainy'].sum()}")
    print(f"Days with no foraging: {(weather_df['foraging_modifier'] == 0).sum()}")
    print(f"Average temperature: {weather_df['temp_avg'].mean():.1f}°C")

    # Run simulation WITHOUT weather (ideal conditions)
    print("\n--- Running simulation WITHOUT weather effects (ideal) ---")
    sim_ideal = SeasonalBeeSimulator(
        calendar=BAIA_MARE_CALENDAR,
        start_date=(3, 1),
        base_egg_laying_rate=1100,
        base_attrition_rate=600,
        total_frames=10,
        initial_brood_frames=6
    )
    results_ideal = sim_ideal.run_simulation(num_days=270).to_dataframes()

    # Run simulation WITH weather (realistic)
    print("\n--- Running simulation WITH weather effects (realistic) ---")
    sim_weather = SeasonalBeeSimulator(
        calendar=BAIA_MARE_CALENDAR,
        start_date=(3, 1),
        base_egg_laying_rate=1100,
        base_attrition_rate=600,
        total_frames=10,
        initial_brood_frames=6
    )
    results_weather = simulate_with_weather(sim_weather, weather_df, num_days=270)

    # Create comparison plot
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle('Weather Impact on Bee Colony: Ideal vs Realistic Conditions',
                 fontsize=16, fontweight='bold')

    days = results_ideal['population'].index.values

    # Adult population comparison
    ax1 = axes[0, 0]
    ax1.plot(days, results_ideal['population']['adult_bees'], 'g-',
             linewidth=2, label='Ideal (no weather)')
    ax1.plot(days, results_weather['population']['adult_bees'], 'b-',
             linewidth=2, label='Realistic (with weather)', alpha=0.8)
    ax1.set_xlabel('Days')
    ax1.set_ylabel('Adult Bees')
    ax1.set_title('Adult Population: Weather Impact')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Brood comparison
    ax2 = axes[0, 1]
    ax2.plot(days, results_ideal['population']['total_brood'], 'g-',
             linewidth=2, label='Ideal')
    ax2.plot(days, results_weather['population']['total_brood'], 'b-',
             linewidth=2, label='Realistic', alpha=0.8)
    ax2.set_xlabel('Days')
    ax2.set_ylabel('Total Brood')
    ax2.set_title('Brood Population: Weather Impact')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Temperature profile
    ax3 = axes[1, 0]
    ax3.fill_between(days, weather_df['temp_min'], weather_df['temp_max'],
                     alpha=0.3, color='orange', label='Daily range')
    ax3.plot(days, weather_df['temp_avg'], 'r-', linewidth=2, label='Average')
    ax3.axhline(y=15, color='blue', linestyle='--', linewidth=1, label='Min foraging (15°C)')
    ax3.axhline(y=10, color='purple', linestyle='--', linewidth=1, label='Min brood (10°C)')
    ax3.set_xlabel('Days')
    ax3.set_ylabel('Temperature (°C)')
    ax3.set_title('Daily Temperature Profile')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # Foraging conditions
    ax4 = axes[1, 1]
    ax4.fill_between(days, weather_df['foraging_modifier'],
                     alpha=0.6, color='gold', label='Foraging possible')
    ax4.scatter(weather_df[weather_df['is_rainy']].index,
               [0.02] * weather_df['is_rainy'].sum(),
               color='blue', marker='|', s=100, label='Rainy days')
    ax4.set_xlabel('Days')
    ax4.set_ylabel('Foraging Activity (0-1)')
    ax4.set_title('Weather-Based Foraging Conditions')
    ax4.set_ylim(-0.05, 1.05)
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Honey production comparison
    ax5 = axes[2, 0]
    if 'resources' in results_weather:
        ax5.plot(days, results_ideal['resources']['honey_stores'], 'g-',
                linewidth=2, label='Ideal conditions')
        ax5.plot(days, results_weather['resources']['honey_stores'], 'b-',
                linewidth=2, label='With weather', alpha=0.8)
        ax5.set_xlabel('Days')
        ax5.set_ylabel('Honey Stores (kg)')
        ax5.set_title('Honey Production: Weather Impact')
        ax5.legend()
        ax5.grid(True, alpha=0.3)

    # Population difference over time
    ax6 = axes[2, 1]
    pop_diff = results_ideal['population']['adult_bees'].values - \
               results_weather['population']['adult_bees'].values
    colors = ['red' if x >= 0 else 'green' for x in pop_diff]
    ax6.bar(days, pop_diff, color=colors, alpha=0.6, width=1)
    ax6.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax6.set_xlabel('Days')
    ax6.set_ylabel('Population Loss Due to Weather')
    ax6.set_title('Weather Impact: Population Reduction')
    ax6.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()

    # Print summary
    print("\n=== Impact Summary ===")
    print(f"\nIdeal conditions (no weather):")
    print(f"  Peak population: {results_ideal['population']['adult_bees'].max():,.0f} bees")
    print(f"  Final population: {results_ideal['population'].iloc[-1]['adult_bees']:,.0f} bees")
    if 'resources' in results_ideal:
        print(f"  Final honey: {results_ideal['resources'].iloc[-1]['honey_stores']:.1f} kg")

    print(f"\nRealistic conditions (with weather):")
    print(f"  Peak population: {results_weather['population']['adult_bees'].max():,.0f} bees")
    print(f"  Final population: {results_weather['population'].iloc[-1]['adult_bees']:,.0f} bees")
    if 'resources' in results_weather:
        print(f"  Final honey: {results_weather['resources'].iloc[-1]['honey_stores']:.1f} kg")

    peak_loss = results_ideal['population']['adult_bees'].max() - \
                results_weather['population']['adult_bees'].max()
    final_loss = results_ideal['population'].iloc[-1]['adult_bees'] - \
                 results_weather['population'].iloc[-1]['adult_bees']

    print(f"\nWeather impact:")
    print(f"  Peak population reduction: {peak_loss:,.0f} bees ({peak_loss/results_ideal['population']['adult_bees'].max()*100:.1f}%)")
    print(f"  Final population reduction: {final_loss:,.0f} bees ({final_loss/results_ideal['population'].iloc[-1]['adult_bees']*100:.1f}%)")

    if 'resources' in results_weather and 'resources' in results_ideal:
        honey_loss = results_ideal['resources'].iloc[-1]['honey_stores'] - \
                     results_weather['resources'].iloc[-1]['honey_stores']
        print(f"  Honey production reduction: {honey_loss:.1f} kg")


def simulate_with_weather(simulator: SeasonalBeeSimulator,
                          weather_df: pd.DataFrame,
                          num_days: int) -> dict:
    """
    Run simulation with weather modifiers applied.

    This is a demonstration function showing how weather could be integrated.
    A full integration would modify the SeasonalBeeSimulator class directly.

    Args:
        simulator: Initialized SeasonalBeeSimulator
        weather_df: Weather DataFrame from WeatherModel
        num_days: Number of days to simulate

    Returns:
        Results dictionary from simulator.to_dataframes()
    """
    # For this demonstration, we'll manually apply weather modifiers
    # by adjusting rates day by day

    # Store original rates
    original_egg_rate = simulator.base_egg_laying_rate
    original_attrition = simulator.base_attrition_rate

    # Run simulation day by day with weather adjustments
    for day in range(num_days):
        # Get weather modifiers for this day
        weather_row = weather_df.iloc[day]
        foraging_mod = weather_row['foraging_modifier']
        brood_mod = weather_row['brood_rearing_modifier']

        # Adjust rates for this day
        # Egg laying affected by brood rearing modifier
        simulator.base_egg_laying_rate = int(original_egg_rate * brood_mod)

        # Attrition increases slightly in bad weather (bees venture out anyway)
        if foraging_mod < 0.3:
            # Bad weather: 10% more attrition (risky foraging attempts)
            simulator.base_attrition_rate = int(original_attrition * 1.1)
        else:
            simulator.base_attrition_rate = original_attrition

        # Simulate one day
        simulator.simulate_day(day)

        # Adjust honey production based on foraging conditions
        if hasattr(simulator, 'history') and 'daily_honey_production' in simulator.history:
            # Reduce honey production by foraging modifier
            if len(simulator.history['daily_honey_production']) > 0:
                current_production = simulator.history['daily_honey_production'][-1]
                adjusted_production = current_production * foraging_mod
                simulator.history['daily_honey_production'][-1] = adjusted_production

                # Adjust honey stores accordingly
                if len(simulator.history['honey_stores']) > 0:
                    production_loss = current_production - adjusted_production
                    simulator.history['honey_stores'][-1] -= production_loss
                    simulator.honey_stores -= production_loss

    # Restore original rates
    simulator.base_egg_laying_rate = original_egg_rate
    simulator.base_attrition_rate = original_attrition

    # Return results
    return simulator.to_dataframes()


def print_weather_statistics(weather_df: pd.DataFrame):
    """Print detailed weather statistics."""
    print("\n=== Weather Statistics ===")
    print(f"Total days: {len(weather_df)}")
    print(f"\nTemperature:")
    print(f"  Average: {weather_df['temp_avg'].mean():.1f}°C")
    print(f"  Range: {weather_df['temp_min'].min():.1f}°C to {weather_df['temp_max'].max():.1f}°C")
    print(f"  Days below 10°C (no brood): {(weather_df['temp_avg'] < 10).sum()}")
    print(f"  Days below 15°C (no foraging): {(weather_df['temp_max'] < 15).sum()}")
    print(f"  Days 15-20°C (limited foraging): {((weather_df['temp_avg'] >= 15) & (weather_df['temp_avg'] < 20)).sum()}")
    print(f"  Days 20-30°C (optimal): {((weather_df['temp_avg'] >= 20) & (weather_df['temp_avg'] <= 30)).sum()}")

    print(f"\nPrecipitation:")
    print(f"  Rainy days: {weather_df['is_rainy'].sum()} ({weather_df['is_rainy'].sum()/len(weather_df)*100:.1f}%)")
    print(f"  Total: {weather_df['precipitation_mm'].sum():.0f} mm")
    print(f"  Average per rainy day: {weather_df[weather_df['is_rainy']]['precipitation_mm'].mean():.1f} mm")

    print(f"\nSunlight:")
    print(f"  Average daylight: {weather_df['daylight_hours'].mean():.1f} hours")
    print(f"  Average useful foraging hours: {weather_df['useful_sunlight_hours'].mean():.1f} hours")

    print(f"\nForaging Conditions:")
    print(f"  No foraging possible: {(weather_df['foraging_modifier'] == 0).sum()} days")
    print(f"  Limited foraging (0-50%): {((weather_df['foraging_modifier'] > 0) & (weather_df['foraging_modifier'] < 0.5)).sum()} days")
    print(f"  Good foraging (50-100%): {(weather_df['foraging_modifier'] >= 0.5).sum()} days")
    print(f"  Average foraging modifier: {weather_df['foraging_modifier'].mean():.3f}")

    print(f"\nBrood Rearing:")
    print(f"  No new brood possible: {(weather_df['brood_rearing_modifier'] == 0).sum()} days")
    print(f"  Reduced brood rearing: {((weather_df['brood_rearing_modifier'] > 0) & (weather_df['brood_rearing_modifier'] < 1.0)).sum()} days")
    print(f"  Normal brood rearing: {(weather_df['brood_rearing_modifier'] == 1.0).sum()} days")
    print(f"  Average brood modifier: {weather_df['brood_rearing_modifier'].mean():.3f}")


if __name__ == "__main__":
    print("=" * 80)
    print("WEATHER INTEGRATION EXAMPLE")
    print("Demonstrating realistic colony dynamics with weather effects")
    print("=" * 80)

    # Generate and display weather statistics
    weather_model = create_baia_mare_weather(start_date=(3, 1), seed=42)
    weather_results = weather_model.to_dataframes(num_days=270)
    weather_df = weather_results['weather']

    print_weather_statistics(weather_df)

    # Run comparison scenario
    scenario_weather_impact_comparison()

    print("\n" + "=" * 80)
    print("INTEGRATION NOTES:")
    print("=" * 80)
    print("""
This example demonstrates weather integration via post-processing modifiers.

For production use, weather should be integrated directly into SeasonalBeeSimulator:

1. Add weather parameter to __init__:
   def __init__(self, calendar, weather_model=None, ...):

2. In simulate_day(), apply weather modifiers:
   calendar_modifier = calendar.get_daily_factors(day)
   weather_modifier = weather_model.get_daily_factors(day) if weather_model else 1.0
   final_modifier = calendar_modifier * weather_modifier

3. Track weather data in history:
   self.history['weather_temp'] = []
   self.history['weather_foraging_mod'] = []

4. Adjust honey production based on foraging_modifier:
   effective_nectar = nectar_availability * foraging_modifier

5. Add weather DataFrame to to_dataframes() output

This provides realistic colony dynamics while maintaining clean separation of concerns.
""")
