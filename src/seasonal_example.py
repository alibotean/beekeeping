"""
Seasonal Bee Simulator - Example Usage

This script demonstrates the seasonal bee simulator with various scenarios
showing how the calendar-driven modulation affects colony dynamics throughout
the year in the Maramures region (Baia Mare).

Run this script to see:
1. Full year simulation with seasonal effects
2. Comparison between seasonal and fixed-rate simulators
3. Key flow periods and their impact on colony dynamics
"""

from seasonal_bee_simulator import SeasonalBeeSimulator
from bee_population import BeeHiveSimulator
from maramures_calendar import BAIA_MARE_CALENDAR, CHIUZBAIA_CALENDAR, date_to_day_of_year
import matplotlib.pyplot as plt


def scenario_1_full_year():
    """
    Scenario 1: Full growing season (March - November)

    This scenario simulates a complete beekeeping season in Baia Mare,
    starting from early spring (March 1) through late fall (November 26).

    Expected dynamics:
    - Slow buildup in March (Hazelnut/Willow pollen triggers laying)
    - Rapid expansion in April (Plum flow: 1.3x egg rate)
    - Peak egg laying in May (Acacia: 1.4x egg rate)
    - Population peak in June (Linden/Raspberry flows)
    - High mortality in July-August (foraging stress: 0.6-0.7x attrition)
    - Decline in September-October (reduced laying: 0.2-0.4x egg rate)
    """
    print("\n" + "=" * 80)
    print("SCENARIO 1: Full Growing Season (March 1 - November 26)")
    print("=" * 80)

    sim = SeasonalBeeSimulator(
        calendar=BAIA_MARE_CALENDAR,
        start_date=(3, 1),           # March 1st
        base_egg_laying_rate=1100,   # Average queen
        base_attrition_rate=600,     # Base mortality (modulated by calendar)
        total_frames=10,
        initial_brood_frames=6
    )

    # Run for 270 days (approximately 9 months)
    sim.run_simulation(num_days=270)

    # Print summary
    sim.print_seasonal_summary()

    # Show plots
    sim.plot_results()


def scenario_2_comparison():
    """
    Scenario 2: Seasonal vs Fixed-Rate Comparison

    This scenario compares the seasonal simulator (with calendar modulation)
    against the traditional fixed-rate simulator to show the impact of
    seasonal effects on colony dynamics.

    The seasonal simulator should show:
    - More realistic seasonal variation
    - Natural spring buildup and fall decline
    - Population peaks aligned with major flows
    """
    print("\n" + "=" * 80)
    print("SCENARIO 2: Seasonal vs Fixed-Rate Comparison (120 days)")
    print("=" * 80)

    # Seasonal simulator (March 1 - June 29)
    print("\n--- Running Seasonal Simulator ---")
    seasonal_sim = SeasonalBeeSimulator(
        calendar=BAIA_MARE_CALENDAR,
        start_date=(3, 1),
        base_egg_laying_rate=1100,
        base_attrition_rate=600,
        total_frames=10,
        initial_brood_frames=6
    )
    seasonal_sim.run_simulation(num_days=120)

    # Fixed-rate simulator (for comparison)
    print("\n--- Running Fixed-Rate Simulator ---")
    fixed_sim = BeeHiveSimulator(
        egg_laying_rate=1100,  # Constant rate (no modulation)
        attrition_rate=600,    # Constant rate (no modulation)
        total_frames=10,
        initial_brood_frames=6
    )
    fixed_sim.run_simulation(num_days=120)

    # Create comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Seasonal vs Fixed-Rate Simulator Comparison', fontsize=16, fontweight='bold')

    days = seasonal_sim.history['day']
    dates = seasonal_sim.history['calendar_date']

    # Adult population comparison
    ax1 = axes[0, 0]
    ax1.plot(days, seasonal_sim.history['adult_bees'], 'b-', linewidth=2, label='Seasonal')
    ax1.plot(days, fixed_sim.history['adult_bees'], 'r--', linewidth=2, label='Fixed-Rate')
    ax1.set_xlabel('Days')
    ax1.set_ylabel('Adult Bees')
    ax1.set_title('Adult Bee Population Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Brood comparison
    ax2 = axes[0, 1]
    ax2.plot(days, seasonal_sim.history['total_brood'], 'g-', linewidth=2, label='Seasonal')
    ax2.plot(days, fixed_sim.history['total_brood'], 'orange', linestyle='--',
            linewidth=2, label='Fixed-Rate')
    ax2.set_xlabel('Days')
    ax2.set_ylabel('Total Brood')
    ax2.set_title('Total Brood Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Seasonal egg laying rate
    ax3 = axes[1, 0]
    ax3.plot(days, seasonal_sim.history['effective_egg_rate'], 'purple', linewidth=2)
    ax3.axhline(y=1100, color='red', linestyle='--', linewidth=2, label='Fixed Rate (1100)')
    ax3.set_xlabel('Days')
    ax3.set_ylabel('Eggs Laid per Day')
    ax3.set_title('Seasonal Egg Laying Rate (Modulated)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Forage availability
    ax4 = axes[1, 1]
    ax4.plot(days, seasonal_sim.history['nectar_availability'], 'gold',
            linewidth=2, label='Nectar', alpha=0.8)
    ax4.plot(days, seasonal_sim.history['pollen_availability'], 'brown',
            linewidth=2, label='Pollen', alpha=0.8)
    ax4.set_xlabel('Days')
    ax4.set_ylabel('Availability (0-1)')
    ax4.set_title('Forage Availability (Seasonal Only)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(-0.05, 1.05)

    plt.tight_layout()
    plt.show()

    # Print comparison summary
    print("\n=== Comparison Summary ===")
    print(f"Seasonal simulator final population: {seasonal_sim.adult_bees:,} bees")
    print(f"Fixed-rate simulator final population: {fixed_sim.adult_bees:,} bees")
    print(f"Difference: {seasonal_sim.adult_bees - fixed_sim.adult_bees:+,} bees")


def scenario_3_key_dates():
    """
    Scenario 3: Key Flow Periods Inspection

    This scenario demonstrates how to inspect the calendar to understand
    what flows are active on key dates and how they affect colony behavior.

    This is useful for planning beekeeping activities:
    - When to start spring stimulation feeding
    - When to expect swarm pressure (high egg laying)
    - When to harvest honey
    - When to prepare for winter
    """
    print("\n" + "=" * 80)
    print("SCENARIO 3: Key Flow Periods and Colony Dynamics")
    print("=" * 80)

    # Define key dates throughout the season
    key_dates = [
        (2, 20, "Hazelnut/Alder - First pollen"),
        (3, 20, "Willow begins - Nectar + pollen"),
        (4, 10, "Plum bloom - Major buildup"),
        (5, 5, "Acacia peak - Maximum flow"),
        (5, 20, "May Gap - Potential dearth"),
        (6, 1, "Raspberry begins - Reliable flow"),
        (6, 10, "Linden begins - Harvest time"),
        (7, 15, "Honeydew starts - High mortality"),
        (8, 1, "Summer dearth - Critical period"),
        (9, 1, "Fall transition - Winding down"),
        (11, 1, "Pre-winter - Clustering"),
    ]

    print("\nKey Dates and Expected Colony Behavior:")
    print("-" * 80)

    for month, day, description in key_dates:
        doy = date_to_day_of_year(month, day)
        flows = BAIA_MARE_CALENDAR.get_active_flows(doy)
        factors = BAIA_MARE_CALENDAR.get_daily_factors(doy)
        date_str = BAIA_MARE_CALENDAR.day_of_year_to_date_string(doy)

        print(f"\n{description} ({date_str}):")
        print(f"  Active flows: {', '.join(factors['active_flow_names']) if factors['active_flow_names'] else 'None (Dearth)'}")
        print(f"  Nectar: {factors['nectar_availability']:.2f}  Pollen: {factors['pollen_availability']:.2f}")
        print(f"  Egg rate modifier: {factors['egg_rate_modifier']:.2f}x (Base 1100 → ~{int(1100 * factors['egg_rate_modifier'])} eggs/day)")
        print(f"  Attrition modifier: {factors['attrition_modifier']:.2f}x (Base 300 → ~{int(300 * factors['attrition_modifier'])} deaths/day)")

        # Provide beekeeper action recommendation
        if factors['egg_rate_modifier'] >= 1.3:
            print(f"  🐝 Action: High swarm risk - add frames, consider splits")
        elif factors['egg_rate_modifier'] <= 0.4:
            print(f"  🐝 Action: Prepare for winter - ensure adequate stores")
        elif factors['nectar_availability'] >= 0.8:
            print(f"  🐝 Action: Major flow - add supers, monitor for harvest")
        elif factors['nectar_availability'] <= 0.3 and factors['egg_rate_modifier'] > 0.5:
            print(f"  🐝 Action: Dearth period - consider supplemental feeding")


def scenario_4_spring_buildup():
    """
    Scenario 4: Spring Buildup Analysis (February - May)

    This scenario focuses on the critical spring buildup period, showing
    how the colony expands from winter cluster through the major spring flows.

    This period includes:
    - Hazelnut/Alder pollen (triggers laying)
    - Willow (first nectar)
    - Plum (rapid expansion)
    - Acacia (peak production)
    """
    print("\n" + "=" * 80)
    print("SCENARIO 4: Spring Buildup Analysis (February 20 - May 31)")
    print("=" * 80)

    sim = SeasonalBeeSimulator(
        calendar=BAIA_MARE_CALENDAR,
        start_date=(2, 20),          # Start at Hazelnut/Alder
        base_egg_laying_rate=1100,
        base_attrition_rate=600,
        total_frames=12,             # More frames for expansion
        initial_brood_frames=4       # Starting from winter cluster
    )

    # Simulate 100 days (Feb 20 - May 31)
    sim.run_simulation(num_days=100)

    # Print summary
    sim.print_seasonal_summary()

    # Plot results
    sim.plot_results()

    print("\nSpring Buildup Notes:")
    print("- Population should grow rapidly during Plum and Acacia flows")
    print("- Egg laying rate increases from ~660/day (0.6x) to ~1540/day (1.4x)")
    print("- Watch for swarm pressure during late April / early May")
    print("- Add frames during fruit tree blooms to prevent congestion")


def scenario_5_chiuzbaia_full_season():
    """
    Scenario 5: Full Growing Season in Chiuzbaia (Mountain Location)

    This scenario demonstrates the mountain apiary dynamics with:
    - Phenological delay (~15 days later than Baia Mare)
    - Enhanced Raspberry flow (fills the May Gap)
    - Extended Fireweed and Honeydew flows
    - Stronger meadow flora presence
    - Cooler temperatures = higher altitude foraging stress

    Expected dynamics:
    - Later spring buildup (delayed by 15 days)
    - Raspberry provides "Green Bridge" between fruit trees and Linden
    - Continuous summer flow from meadows, fireweed, honeydew
    - Less summer dearth compared to Baia Mare
    - Population should stay strong through August
    """
    print("\n" + "=" * 80)
    print("SCENARIO 5: Chiuzbaia Mountain Apiary (March 1 - November 26)")
    print("=" * 80)

    sim = SeasonalBeeSimulator(
        calendar=CHIUZBAIA_CALENDAR,
        start_date=(3, 1),           # March 1st
        base_egg_laying_rate=1100,   # Average queen
        base_attrition_rate=600,     # Base mortality
        total_frames=10,
        initial_brood_frames=6
    )

    # Run for 270 days (approximately 9 months)
    sim.run_simulation(num_days=270)

    # Print summary
    sim.print_seasonal_summary()

    # Show plots
    sim.plot_results()


def scenario_6_location_comparison():
    """
    Scenario 6: Baia Mare vs Chiuzbaia Location Comparison

    This scenario runs identical colonies at both locations to demonstrate
    the strategic advantages of the "vertical migration" approach mentioned
    in your research document.

    Key insights:
    - Baia Mare: Early spring buildup, strong Acacia flow (weather-dependent)
    - Chiuzbaia: Later start, reliable Raspberry, extended summer flows
    - "Green Bridge": Raspberry in Chiuzbaia fills Baia Mare's May Gap
    - Cooler mountain temps = sustained flows through summer
    """
    print("\n" + "=" * 80)
    print("SCENARIO 6: Location Comparison - Baia Mare vs Chiuzbaia")
    print("=" * 80)

    # Baia Mare simulation
    print("\n--- Running Baia Mare Simulation (220m altitude) ---")
    bm_sim = SeasonalBeeSimulator(
        calendar=BAIA_MARE_CALENDAR,
        start_date=(3, 1),
        base_egg_laying_rate=1100,
        base_attrition_rate=600,
        total_frames=10,
        initial_brood_frames=6
    )
    bm_sim.run_simulation(num_days=200)  # Mar 1 - Sep 17

    # Chiuzbaia simulation
    print("\n--- Running Chiuzbaia Simulation (575m altitude) ---")
    ch_sim = SeasonalBeeSimulator(
        calendar=CHIUZBAIA_CALENDAR,
        start_date=(3, 1),
        base_egg_laying_rate=1100,
        base_attrition_rate=600,
        total_frames=10,
        initial_brood_frames=6
    )
    ch_sim.run_simulation(num_days=200)  # Mar 1 - Sep 17

    # Create comparison visualization
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle('Location Comparison: Baia Mare (220m) vs Chiuzbaia (575m)',
                 fontsize=16, fontweight='bold')

    days = bm_sim.history['day']

    # Adult population comparison
    ax1 = axes[0, 0]
    ax1.plot(days, bm_sim.history['adult_bees'], 'b-', linewidth=2, label='Baia Mare')
    ax1.plot(days, ch_sim.history['adult_bees'], 'g-', linewidth=2, label='Chiuzbaia')
    ax1.set_xlabel('Days')
    ax1.set_ylabel('Adult Bees')
    ax1.set_title('Adult Population Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Brood comparison
    ax2 = axes[0, 1]
    ax2.plot(days, bm_sim.history['total_brood'], 'b-', linewidth=2, label='Baia Mare')
    ax2.plot(days, ch_sim.history['total_brood'], 'g-', linewidth=2, label='Chiuzbaia')
    ax2.set_xlabel('Days')
    ax2.set_ylabel('Total Brood')
    ax2.set_title('Brood Population Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Egg laying rate comparison
    ax3 = axes[1, 0]
    ax3.plot(days, bm_sim.history['effective_egg_rate'], 'b-', linewidth=2, label='Baia Mare')
    ax3.plot(days, ch_sim.history['effective_egg_rate'], 'g-', linewidth=2, label='Chiuzbaia')
    ax3.set_xlabel('Days')
    ax3.set_ylabel('Eggs per Day')
    ax3.set_title('Egg Laying Rate Comparison')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Attrition rate comparison
    ax4 = axes[1, 1]
    ax4.plot(days, bm_sim.history['effective_attrition'], 'b-', linewidth=2, label='Baia Mare')
    ax4.plot(days, ch_sim.history['effective_attrition'], 'g-', linewidth=2, label='Chiuzbaia')
    ax4.set_xlabel('Days')
    ax4.set_ylabel('Deaths per Day')
    ax4.set_title('Attrition Rate Comparison')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Nectar availability comparison
    ax5 = axes[2, 0]
    ax5.plot(days, bm_sim.history['nectar_availability'], 'b-', linewidth=2, label='Baia Mare')
    ax5.plot(days, ch_sim.history['nectar_availability'], 'g-', linewidth=2, label='Chiuzbaia')
    ax5.set_xlabel('Days')
    ax5.set_ylabel('Nectar Availability (0-1)')
    ax5.set_title('Nectar Flow Comparison')
    ax5.set_ylim(-0.05, 1.05)
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # Population difference
    ax6 = axes[2, 1]
    pop_diff = [ch - bm for ch, bm in zip(ch_sim.history['adult_bees'], bm_sim.history['adult_bees'])]
    colors = ['green' if x >= 0 else 'red' for x in pop_diff]
    ax6.bar(days, pop_diff, color=colors, alpha=0.6)
    ax6.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax6.set_xlabel('Days')
    ax6.set_ylabel('Population Difference (Chiuzbaia - Baia Mare)')
    ax6.set_title('Chiuzbaia Advantage/Disadvantage')
    ax6.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()

    # Print summary comparison
    print("\n=== Location Comparison Summary ===")
    print(f"\nBaia Mare (220m):")
    print(f"  Peak population: {max(bm_sim.history['adult_bees']):,} bees")
    print(f"  Final population: {bm_sim.adult_bees:,} bees")
    print(f"  Peak egg rate: {max(bm_sim.history['effective_egg_rate'])} eggs/day")

    print(f"\nChiuzbaia (575m):")
    print(f"  Peak population: {max(ch_sim.history['adult_bees']):,} bees")
    print(f"  Final population: {ch_sim.adult_bees:,} bees")
    print(f"  Peak egg rate: {max(ch_sim.history['effective_egg_rate'])} eggs/day")

    print(f"\n✓ Phenological offset demonstrates 'vertical migration' advantage")
    print(f"✓ Chiuzbaia Raspberry flow fills Baia Mare's May Gap")
    print(f"✓ Extended mountain flows provide sustained production")


def scenario_7_pastoral_movement_strategy():
    """
    Scenario 7: Pastoral Movement - Strategic Hive Relocation

    This scenario demonstrates the "vertical migration" strategy from your
    research document: using Baia Mare as the "Incubator" for early spring
    buildup, then moving to Chiuzbaia as the "Granary" for sustained summer flows.

    Strategy:
    1. Start in Baia Mare: Take advantage of early spring (Willow, Plum, Acacia)
    2. Move to Chiuzbaia in late May: Catch Raspberry → Linden → Fireweed sequence
    3. Harvest mountain honey (Raspberry, Linden, Fireweed, Honeydew)

    Note: This example shows the concept. In practice, you would simulate moving
    by switching calendars mid-simulation (future feature).
    """
    print("\n" + "=" * 80)
    print("SCENARIO 7: Pastoral Movement Strategy (Conceptual)")
    print("=" * 80)

    print("\nPhase 1: Spring Buildup in Baia Mare (Mar 1 - May 20)")
    print("-" * 80)

    # Phase 1: Baia Mare early season
    bm_sim = SeasonalBeeSimulator(
        calendar=BAIA_MARE_CALENDAR,
        start_date=(3, 1),
        base_egg_laying_rate=1100,
        base_attrition_rate=600,
        total_frames=10,
        initial_brood_frames=6
    )
    bm_sim.run_simulation(num_days=80)  # 80 days = Mar 1 to May 20

    print(f"\nBaia Mare Result (May 20):")
    print(f"  Adult bees: {bm_sim.adult_bees:,}")
    print(f"  Total brood: {bm_sim.get_current_brood_count():,}")
    print(f"  Status: Strong colony ready for Raspberry flow")

    print("\n\nPhase 2: Summer Production in Chiuzbaia (May 25 - Sep 15)")
    print("-" * 80)
    print("Conceptual move: Hives transported to mountain location...")

    # Phase 2: Chiuzbaia summer (would continue from Baia Mare state)
    # For demo, start a new simulation from the approximate Baia Mare endpoint
    ch_sim = SeasonalBeeSimulator(
        calendar=CHIUZBAIA_CALENDAR,
        start_date=(5, 25),  # Start at Raspberry flow
        base_egg_laying_rate=1100,
        base_attrition_rate=600,
        total_frames=10,
        initial_brood_frames=8  # More frames after spring expansion
    )
    ch_sim.run_simulation(num_days=113)  # May 25 - Sep 15

    print(f"\nChiuzbaia Result (Sep 15):")
    print(f"  Adult bees: {ch_sim.adult_bees:,}")
    print(f"  Total brood: {ch_sim.get_current_brood_count():,}")
    print(f"  Status: Summer harvest complete")

    print("\n=== Pastoral Movement Strategy Summary ===")
    print("✓ Baia Mare (Mar-May): Early spring buildup + Acacia harvest")
    print("✓ Move to Chiuzbaia (late May): Before Raspberry flow")
    print("✓ Chiuzbaia (Jun-Sep): Raspberry + Linden + Fireweed + Honeydew")
    print("✓ Result: Extended harvest season, filled May Gap, avoided summer dearth")
    print("\nKey insight: The 'vertical migration' exploits phenological offset")
    print("to extend forage availability from April through September!")


def main():
    """
    Main function to run all example scenarios.

    Comment out scenarios you don't want to run.
    """
    print("=" * 80)
    print("SEASONAL BEE SIMULATOR - EXAMPLE SCENARIOS")
    print("Maramures Region - Two Locations: Baia Mare (220m) & Chiuzbaia (575m)")
    print("=" * 80)

    # Run scenarios
    # Uncomment the scenarios you want to run:

    # BAIA MARE SCENARIOS
    scenario_1_full_year()           # Full growing season (Baia Mare)
    # scenario_2_comparison()         # Seasonal vs fixed-rate
    # scenario_3_key_dates()          # Key flow periods inspection
    # scenario_4_spring_buildup()     # Spring buildup analysis

    # CHIUZBAIA SCENARIOS (NEW!)
    # scenario_5_chiuzbaia_full_season()      # Full season in mountains
    # scenario_6_location_comparison()        # Compare both locations side-by-side
    # scenario_7_pastoral_movement_strategy() # Vertical migration strategy


if __name__ == "__main__":
    main()
