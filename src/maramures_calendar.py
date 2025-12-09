"""
Maramures Honey Flow Calendar

This module defines the seasonal flow periods for the Baia Mare region (220m altitude)
based on the comprehensive research document "Maramureș Honey Flow Calendar Research.md".

The calendar provides day-by-day modulation factors for queen egg-laying rates and
bee attrition rates, allowing realistic simulation of colony population dynamics
throughout the year.

Usage:
    from maramures_calendar import BAIA_MARE_CALENDAR

    # Get factors for a specific day of year
    factors = BAIA_MARE_CALENDAR.get_daily_factors(100)  # Day 100 = April 10
    print(f"Egg rate modifier: {factors['egg_rate_modifier']}")
    print(f"Active flows: {factors['active_flow_names']}")
"""

from dataclasses import dataclass
from typing import List
import datetime


@dataclass
class FlowPeriod:
    """
    Represents a nectar/pollen flow period in the beekeeping calendar.

    Attributes:
        name: Common name of the flow (e.g., "Plum (Prun)", "Acacia (Salcâm)")
        start_day: Day of year when flow begins (1-365)
        end_day: Day of year when flow ends (1-365)
        nectar_intensity: Relative nectar availability (0.0-1.0)
        pollen_intensity: Relative pollen availability (0.0-1.0)
        egg_rate_modifier: Multiplier for base egg-laying rate (0.0-1.4)
                          1.0 = normal, >1.0 = increased laying, <1.0 = reduced
        attrition_modifier: Multiplier for base attrition rate (0.0-0.8)
                           1.0 = normal, <1.0 = reduced mortality, >1.0 = increased
    """
    name: str
    start_day: int
    end_day: int
    nectar_intensity: float
    pollen_intensity: float
    egg_rate_modifier: float
    attrition_modifier: float

    def is_active(self, day_of_year: int) -> bool:
        """Check if this flow period is active on the given day of year"""
        return self.start_day <= day_of_year <= self.end_day


class MaramuresCalendar:
    """
    Calendar system for tracking seasonal nectar/pollen flows in Maramures.

    This class manages the complete annual cycle of flow periods and provides
    daily modulation factors for bee population dynamics.
    """

    def __init__(self, flow_periods: List[FlowPeriod], location_name: str = "Baia Mare"):
        """
        Initialize calendar with flow periods.

        Args:
            flow_periods: List of FlowPeriod objects defining the annual cycle
            location_name: Name of the location for reference
        """
        self.flow_periods = flow_periods
        self.location_name = location_name

    def get_active_flows(self, day_of_year: int) -> List[FlowPeriod]:
        """
        Get all flow periods active on the specified day.

        Args:
            day_of_year: Day of year (1-365)

        Returns:
            List of active FlowPeriod objects
        """
        return [flow for flow in self.flow_periods if flow.is_active(day_of_year)]

    def get_daily_factors(self, day_of_year: int) -> dict:
        """
        Get modulation factors for the specified day of year.

        When multiple flows are active simultaneously, takes the MAXIMUM value
        for each factor. This models the colony responding to the best available
        resource at any given time.

        Args:
            day_of_year: Day of year (1-365)

        Returns:
            Dictionary with keys:
                - nectar_availability: 0.0-1.0
                - pollen_availability: 0.0-1.0
                - egg_rate_modifier: multiplier for base egg-laying rate
                - attrition_modifier: multiplier for base attrition rate
                - active_flow_names: list of active flow names
        """
        active_flows = self.get_active_flows(day_of_year)

        if not active_flows:
            # No active flows - minimal dearth period
            return {
                'nectar_availability': 0.1,
                'pollen_availability': 0.2,
                'egg_rate_modifier': 0.4,
                'attrition_modifier': 0.3,
                'active_flow_names': []
            }

        # Take maximum of each factor across all active flows
        return {
            'nectar_availability': max(f.nectar_intensity for f in active_flows),
            'pollen_availability': max(f.pollen_intensity for f in active_flows),
            'egg_rate_modifier': max(f.egg_rate_modifier for f in active_flows),
            'attrition_modifier': max(f.attrition_modifier for f in active_flows),
            'active_flow_names': [f.name for f in active_flows]
        }

    def day_of_year_to_date_string(self, day_of_year: int) -> str:
        """
        Convert day of year to readable date string.

        Args:
            day_of_year: Day of year (1-365)

        Returns:
            Date string in format "Mon DD" (e.g., "Mar 15")
        """
        # Use a non-leap year reference (2023)
        base = datetime.date(2023, 1, 1)
        target = base + datetime.timedelta(days=day_of_year - 1)
        return target.strftime("%b %d")


# Define all 20 flow periods for Baia Mare based on research document
# Source: "Maramureș Honey Flow Calendar Research.md" Table (pages 152-168)

_BAIA_MARE_FLOW_PERIODS = [
    # Winter Dormancy (Jan 1 - Feb 19)
    FlowPeriod(
        name="Winter Dormancy",
        start_day=1,      # Jan 1
        end_day=50,       # Feb 19
        nectar_intensity=0.0,
        pollen_intensity=0.0,
        egg_rate_modifier=0.05,
        attrition_modifier=0.10
    ),

    # Hazelnut/Alder - First pollen influx (Feb 20 - Mar 1)
    FlowPeriod(
        name="Hazelnut/Alder",
        start_day=51,     # Feb 20
        end_day=60,       # Mar 1
        nectar_intensity=0.1,
        pollen_intensity=0.7,
        egg_rate_modifier=0.6,
        attrition_modifier=0.15
    ),

    # Willow (Salcia) - Nectar + Pollen (Mar 20 - Apr 3)
    FlowPeriod(
        name="Willow (Salcia)",
        start_day=79,     # Mar 20
        end_day=93,       # Apr 3
        nectar_intensity=0.4,
        pollen_intensity=0.8,
        egg_rate_modifier=0.8,
        attrition_modifier=0.18
    ),

    # Early Spring Buildup - Dandelion, early fruit (Apr 4 - Apr 9)
    FlowPeriod(
        name="Early Spring Buildup",
        start_day=94,     # Apr 4
        end_day=99,       # Apr 9
        nectar_intensity=0.3,
        pollen_intensity=0.6,
        egg_rate_modifier=1.0,
        attrition_modifier=0.20
    ),

    # Plum (Prun) - Major buildup flow (Apr 10 - Apr 19)
    FlowPeriod(
        name="Plum (Prun)",
        start_day=100,    # Apr 10
        end_day=109,      # Apr 19
        nectar_intensity=0.7,
        pollen_intensity=0.9,
        egg_rate_modifier=1.3,
        attrition_modifier=0.20
    ),

    # Late Fruit Trees - Apple, Cherry (Apr 20 - May 4)
    FlowPeriod(
        name="Late Fruit Trees",
        start_day=110,    # Apr 20
        end_day=124,      # May 4
        nectar_intensity=0.6,
        pollen_intensity=0.8,
        egg_rate_modifier=1.3,
        attrition_modifier=0.22
    ),

    # Acacia (Salcâm) - Peak flow (May 5 - May 19)
    FlowPeriod(
        name="Acacia (Salcâm)",
        start_day=125,    # May 5
        end_day=139,      # May 19
        nectar_intensity=1.0,
        pollen_intensity=0.5,
        egg_rate_modifier=1.4,
        attrition_modifier=0.25
    ),

    # May Gap - Potential dearth (May 20 - May 31)
    FlowPeriod(
        name="May Gap",
        start_day=140,    # May 20
        end_day=151,      # May 31
        nectar_intensity=0.2,
        pollen_intensity=0.4,
        egg_rate_modifier=0.8,
        attrition_modifier=0.30
    ),

    # Raspberry (Zmeur) - Reliable flow (Jun 1 - Jun 30)
    # Note: Higher attrition due to intensive foraging
    FlowPeriod(
        name="Raspberry (Zmeur)",
        start_day=152,    # Jun 1
        end_day=181,      # Jun 30
        nectar_intensity=0.8,
        pollen_intensity=0.7,
        egg_rate_modifier=1.2,
        attrition_modifier=1.2  # 360 bees/day (moderate foraging stress)
    ),

    # Linden (Tei) - Large-leaved (Jun 10 - Jun 19)
    # Peak foraging activity increases mortality
    FlowPeriod(
        name="Linden (Tei) - Large-leaved",
        start_day=161,    # Jun 10
        end_day=170,      # Jun 19
        nectar_intensity=0.95,
        pollen_intensity=0.6,
        egg_rate_modifier=1.1,
        attrition_modifier=1.5  # 450 bees/day (intense foraging)
    ),

    # Linden - Small/Silver-leaved (Jun 20 - Jul 4)
    FlowPeriod(
        name="Linden - Small/Silver",
        start_day=171,    # Jun 20
        end_day=185,      # Jul 4
        nectar_intensity=0.95,
        pollen_intensity=0.6,
        egg_rate_modifier=1.0,
        attrition_modifier=1.8  # 540 bees/day (sustained intensive foraging)
    ),

    # Meadow Flora - Continuous background (Jun 1 - Aug 29)
    FlowPeriod(
        name="Meadow Flora",
        start_day=152,    # Jun 1
        end_day=241,      # Aug 29
        nectar_intensity=0.5,
        pollen_intensity=0.7,
        egg_rate_modifier=1.0,
        attrition_modifier=1.5  # 450 bees/day (continuous foraging)
    ),

    # Fireweed (High altitude) - Summer plateau (Jun 15 - Aug 29)
    FlowPeriod(
        name="Fireweed (High Alt)",
        start_day=166,    # Jun 15
        end_day=240,      # Aug 28
        nectar_intensity=0.6,
        pollen_intensity=0.5,
        egg_rate_modifier=1.0,
        attrition_modifier=2.0  # 600 bees/day (high altitude foraging stress)
    ),

    # Honeydew (Mană) - High foraging stress (Jul 15 - Aug 29)
    # Research states: "High foraging stress" with 0.60 attrition in summer
    FlowPeriod(
        name="Honeydew (Mană)",
        start_day=196,    # Jul 15
        end_day=240,      # Aug 28
        nectar_intensity=0.7,
        pollen_intensity=0.3,
        egg_rate_modifier=0.9,
        attrition_modifier=2.3  # 690 bees/day (intensive summer foraging + heat)
    ),

    # Summer Dearth - Heat + robbing (Aug 1 - Aug 20)
    # Peak mortality period: heat stress + robbing
    FlowPeriod(
        name="Summer Dearth",
        start_day=213,    # Aug 1
        end_day=232,      # Aug 20
        nectar_intensity=0.3,
        pollen_intensity=0.3,
        egg_rate_modifier=0.8,
        attrition_modifier=2.7  # 810 bees/day (heat + robbing + dearth stress)
    ),

    # Goldenrod - Fall preparation (Aug 21 - Sep 9)
    FlowPeriod(
        name="Goldenrod",
        start_day=233,    # Aug 21
        end_day=252,      # Sep 9
        nectar_intensity=0.4,
        pollen_intensity=0.5,
        egg_rate_modifier=0.7,
        attrition_modifier=2.0  # 600 bees/day (aging summer bees dying off)
    ),

    # Fall Aster/Ivy - Winding down (Sep 1 - Sep 30)
    FlowPeriod(
        name="Fall Aster/Ivy",
        start_day=244,    # Sep 1
        end_day=273,      # Sep 30
        nectar_intensity=0.3,
        pollen_intensity=0.5,
        egg_rate_modifier=0.4,
        attrition_modifier=1.5  # 450 bees/day (summer bees dying, fall bees emerging)
    ),

    # Late Fall - Final preparation (Oct 1 - Oct 31)
    FlowPeriod(
        name="Late Fall",
        start_day=274,    # Oct 1
        end_day=304,      # Oct 31
        nectar_intensity=0.1,
        pollen_intensity=0.2,
        egg_rate_modifier=0.2,
        attrition_modifier=1.0  # 300 bees/day (normal winter bee mortality)
    ),

    # Pre-Winter - Clustering begins (Nov 1 - Nov 30)
    FlowPeriod(
        name="Pre-Winter",
        start_day=305,    # Nov 1
        end_day=334,      # Nov 30
        nectar_intensity=0.0,
        pollen_intensity=0.0,
        egg_rate_modifier=0.05,
        attrition_modifier=0.25
    ),

    # Winter Cluster (Dec 1 - Dec 31)
    FlowPeriod(
        name="Winter Cluster",
        start_day=335,    # Dec 1
        end_day=365,      # Dec 31
        nectar_intensity=0.0,
        pollen_intensity=0.0,
        egg_rate_modifier=0.0,
        attrition_modifier=0.10
    ),
]


# Pre-configured calendar for Baia Mare (220m altitude)
BAIA_MARE_CALENDAR = MaramuresCalendar(
    flow_periods=_BAIA_MARE_FLOW_PERIODS,
    location_name="Baia Mare (220m)"
)


# Define all 20 flow periods for Chiuzbaia with phenological offset
# Source: "Maramureș Honey Flow Calendar Research.md"
# Chiuzbaia altitude: 350-800m (avg ~575m)
# Phenological delay: ~15 days from Baia Mare (4.3 days per 100m elevation)
# Note: Some flows (Raspberry, Fireweed, Honeydew) are more prominent in mountain location

_CHIUZBAIA_FLOW_PERIODS = [
    # Winter Dormancy (Jan 1 - Mar 5) - Extended due to altitude
    FlowPeriod(
        name="Winter Dormancy",
        start_day=1,      # Jan 1
        end_day=65,       # Mar 6 (+15 days from Baia Mare)
        nectar_intensity=0.0,
        pollen_intensity=0.0,
        egg_rate_modifier=0.05,
        attrition_modifier=0.10
    ),

    # Hazelnut/Alder - First pollen influx (Mar 7 - Mar 16)
    FlowPeriod(
        name="Hazelnut/Alder",
        start_day=66,     # Mar 7 (+15 days)
        end_day=75,       # Mar 16 (+15 days)
        nectar_intensity=0.1,
        pollen_intensity=0.7,
        egg_rate_modifier=0.6,
        attrition_modifier=0.15
    ),

    # Willow (Salcia) - Nectar + Pollen (Apr 4 - Apr 18)
    FlowPeriod(
        name="Willow (Salcia)",
        start_day=94,     # Apr 4 (+15 days)
        end_day=108,      # Apr 18 (+15 days)
        nectar_intensity=0.4,
        pollen_intensity=0.8,
        egg_rate_modifier=0.8,
        attrition_modifier=0.18
    ),

    # Early Spring Buildup - Dandelion, early fruit (Apr 19 - Apr 24)
    FlowPeriod(
        name="Early Spring Buildup",
        start_day=109,    # Apr 19 (+15 days)
        end_day=114,      # Apr 24 (+15 days)
        nectar_intensity=0.3,
        pollen_intensity=0.6,
        egg_rate_modifier=1.0,
        attrition_modifier=0.20
    ),

    # Plum (Prun) - Major buildup flow (Apr 25 - May 4)
    FlowPeriod(
        name="Plum (Prun)",
        start_day=115,    # Apr 25 (+15 days, research says +10 for fruit trees)
        end_day=124,      # May 4 (+15 days)
        nectar_intensity=0.7,
        pollen_intensity=0.9,
        egg_rate_modifier=1.3,
        attrition_modifier=0.20
    ),

    # Late Fruit Trees - Apple, Cherry (May 5 - May 19)
    FlowPeriod(
        name="Late Fruit Trees",
        start_day=125,    # May 5 (+15 days)
        end_day=139,      # May 19 (+15 days)
        nectar_intensity=0.6,
        pollen_intensity=0.8,
        egg_rate_modifier=1.3,
        attrition_modifier=0.22
    ),

    # Acacia (Salcâm) - Limited/delayed in mountains (May 15 - May 30)
    # Note: Less common at higher elevations, if present at all
    FlowPeriod(
        name="Acacia (Salcâm)",
        start_day=135,    # May 15 (+10 days, research mentions May 15-30)
        end_day=150,      # May 30 (+11 days)
        nectar_intensity=0.8,  # Reduced from 1.0 (less reliable in mountains)
        pollen_intensity=0.5,
        egg_rate_modifier=1.3,  # Reduced from 1.4
        attrition_modifier=0.25
    ),

    # May Gap - Shorter in mountains (May 31 - Jun 10)
    FlowPeriod(
        name="May-June Transition",
        start_day=151,    # May 31
        end_day=161,      # Jun 10
        nectar_intensity=0.3,
        pollen_intensity=0.5,
        egg_rate_modifier=0.9,
        attrition_modifier=0.30
    ),

    # Raspberry (Zmeur) - MAJOR FLOW in mountains (May 25 - Jun 30)
    # Research: "Very consistent yielder in mountain valleys"
    # Overlaps with transition period - provides "Green Bridge"
    FlowPeriod(
        name="Raspberry (Zmeur)",
        start_day=145,    # May 25 (starts earlier, research says late May)
        end_day=181,      # Jun 30 (extended duration)
        nectar_intensity=0.9,   # Higher than Baia Mare (0.8)
        pollen_intensity=0.8,   # Higher than Baia Mare (0.7)
        egg_rate_modifier=1.2,
        attrition_modifier=1.2  # Mountain foraging effort
    ),

    # Linden (Tei) - Large-leaved (Jun 24 - Jul 3)
    # Research: +14 days delay for Linden
    FlowPeriod(
        name="Linden (Tei) - Large-leaved",
        start_day=175,    # Jun 24 (+14 days from Baia Mare)
        end_day=184,      # Jul 3 (+14 days)
        nectar_intensity=0.95,
        pollen_intensity=0.6,
        egg_rate_modifier=1.1,
        attrition_modifier=1.5
    ),

    # Linden - Small/Silver-leaved (Jul 4 - Jul 19)
    FlowPeriod(
        name="Linden - Small/Silver",
        start_day=185,    # Jul 4 (+14 days)
        end_day=200,      # Jul 19 (+15 days)
        nectar_intensity=0.95,
        pollen_intensity=0.6,
        egg_rate_modifier=1.0,
        attrition_modifier=1.8
    ),

    # Meadow Flora - Continuous background (Jun 1 - Sep 15)
    # Extended duration in mountains due to altitude staggering
    FlowPeriod(
        name="Meadow Flora (Fânețe)",
        start_day=152,    # Jun 1
        end_day=258,      # Sep 15 (extended)
        nectar_intensity=0.6,   # Higher in mountain meadows
        pollen_intensity=0.8,   # Higher diversity
        egg_rate_modifier=1.0,
        attrition_modifier=1.5
    ),

    # Fireweed (Zburătoare) - MAJOR mountain flow (Jun 15 - Sep 10)
    # Research: "300-600 kg/ha at 800m+, fills summer dearth"
    FlowPeriod(
        name="Fireweed (Zburătoare)",
        start_day=166,    # Jun 15
        end_day=253,      # Sep 10 (extended duration)
        nectar_intensity=0.8,   # Higher than lowlands
        pollen_intensity=0.6,
        egg_rate_modifier=1.0,
        attrition_modifier=2.0  # High altitude foraging
    ),

    # Honeydew (Mană) - PREMIUM mountain flow (Jul 15 - Sep 15)
    # Research: "100-300 kg/ha, cyclical every 3-4 years"
    # Mountain forests ideal for honeydew production
    FlowPeriod(
        name="Honeydew (Mană)",
        start_day=196,    # Jul 15
        end_day=258,      # Sep 15 (extended)
        nectar_intensity=0.8,   # Higher than lowlands
        pollen_intensity=0.3,
        egg_rate_modifier=0.9,
        attrition_modifier=2.3  # Intensive foraging + altitude
    ),

    # Summer continues longer in mountains (less summer dearth)
    # The continuous meadow/fireweed/honeydew fills what would be dearth

    # Goldenrod - Fall preparation (Sep 1 - Sep 20)
    FlowPeriod(
        name="Goldenrod",
        start_day=244,    # Sep 1 (similar timing)
        end_day=263,      # Sep 20 (+11 days)
        nectar_intensity=0.4,
        pollen_intensity=0.5,
        egg_rate_modifier=0.7,
        attrition_modifier=2.0
    ),

    # Fall Aster/Ivy + Autumn Crocus (Sep 10 - Oct 10)
    # Research mentions Autumn Crocus in Chiuzbaia
    FlowPeriod(
        name="Fall Aster/Ivy/Crocus",
        start_day=253,    # Sep 10 (+9 days)
        end_day=283,      # Oct 10 (+10 days)
        nectar_intensity=0.3,
        pollen_intensity=0.5,
        egg_rate_modifier=0.4,
        attrition_modifier=1.5
    ),

    # Late Fall - Final preparation (Oct 11 - Nov 10)
    FlowPeriod(
        name="Late Fall",
        start_day=284,    # Oct 11 (+10 days)
        end_day=314,      # Nov 10 (+10 days)
        nectar_intensity=0.1,
        pollen_intensity=0.2,
        egg_rate_modifier=0.2,
        attrition_modifier=1.0
    ),

    # Pre-Winter - Clustering begins (Nov 11 - Nov 30)
    FlowPeriod(
        name="Pre-Winter",
        start_day=315,    # Nov 11 (+10 days)
        end_day=334,      # Nov 30 (same)
        nectar_intensity=0.0,
        pollen_intensity=0.0,
        egg_rate_modifier=0.05,
        attrition_modifier=0.25
    ),

    # Winter Cluster (Dec 1 - Dec 31)
    FlowPeriod(
        name="Winter Cluster",
        start_day=335,    # Dec 1
        end_day=365,      # Dec 31
        nectar_intensity=0.0,
        pollen_intensity=0.0,
        egg_rate_modifier=0.0,
        attrition_modifier=0.10
    ),
]


# Pre-configured calendar for Chiuzbaia (350-800m altitude, avg ~575m)
CHIUZBAIA_CALENDAR = MaramuresCalendar(
    flow_periods=_CHIUZBAIA_FLOW_PERIODS,
    location_name="Chiuzbaia (575m avg)"
)


# Helper function for converting dates to day of year
def date_to_day_of_year(month: int, day: int) -> int:
    """
    Convert a (month, day) tuple to day of year (1-365).

    Args:
        month: Month (1-12)
        day: Day of month (1-31)

    Returns:
        Day of year (1-365)
    """
    # Days before each month in non-leap year
    days_before_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    return days_before_month[month - 1] + day


if __name__ == "__main__":
    # Example usage and testing
    print("=== Maramures Calendar System ===\n")
    print(f"Two locations configured:")
    print(f"  1. {BAIA_MARE_CALENDAR.location_name} - {len(BAIA_MARE_CALENDAR.flow_periods)} flow periods")
    print(f"  2. {CHIUZBAIA_CALENDAR.location_name} - {len(CHIUZBAIA_CALENDAR.flow_periods)} flow periods")
    print(f"\nPhenological offset: ~10-15 days (Chiuzbaia blooms later)")
    print()

    # Test key dates for both locations
    key_dates = [
        (3, 20, "Willow begins"),
        (4, 10, "Plum bloom"),
        (5, 5, "Acacia peak (Baia Mare)"),
        (5, 25, "Raspberry begins (Chiuzbaia)"),
        (6, 10, "Linden begins (Baia Mare)"),
        (6, 24, "Linden begins (Chiuzbaia)"),
        (7, 15, "Honeydew starts"),
    ]

    print("=" * 90)
    print("COMPARISON: Baia Mare vs Chiuzbaia")
    print("=" * 90)

    for month, day, description in key_dates:
        doy = date_to_day_of_year(month, day)
        date_str = BAIA_MARE_CALENDAR.day_of_year_to_date_string(doy)

        # Baia Mare
        bm_factors = BAIA_MARE_CALENDAR.get_daily_factors(doy)
        # Chiuzbaia
        ch_factors = CHIUZBAIA_CALENDAR.get_daily_factors(doy)

        print(f"\n{description} ({date_str}):")
        print(f"  {'Location':<20} {'Flows':<35} {'Egg Mod':>8} {'Nectar':>7}")
        print(f"  {'-'*20} {'-'*35} {'-'*8} {'-'*7}")

        bm_flows = ', '.join(bm_factors['active_flow_names'][:2]) if bm_factors['active_flow_names'] else 'None'
        ch_flows = ', '.join(ch_factors['active_flow_names'][:2]) if ch_factors['active_flow_names'] else 'None'

        print(f"  {'Baia Mare (220m)':<20} {bm_flows:<35} {bm_factors['egg_rate_modifier']:>7.2f}x {bm_factors['nectar_availability']:>7.2f}")
        print(f"  {'Chiuzbaia (575m)':<20} {ch_flows:<35} {ch_factors['egg_rate_modifier']:>7.2f}x {ch_factors['nectar_availability']:>7.2f}")

    print("\n" + "=" * 90)
