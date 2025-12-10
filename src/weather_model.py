"""
Weather Model for Bee Colony Simulations

This module provides realistic weather patterns for the Maramures region,
modeling temperature, sunlight hours, and precipitation. Weather conditions
directly affect bee foraging activity and queen egg-laying behavior.

Key thresholds:
- Minimum foraging temperature: 15°C
- Minimum brood rearing temperature: 10°C (below this, no new eggs)
- Maximum sunlight hours: varies by day of year (4-16 hours)
- Rain: prevents foraging even if temperature is adequate
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
import math


class WeatherModel:
    """
    Models daily weather conditions affecting bee colony behavior.

    Generates realistic weather patterns for Maramures region (Romania) with:
    - Seasonal temperature variation
    - Day-length based sunlight hours
    - Realistic precipitation patterns
    - Continental climate characteristics

    Weather affects:
    - Foraging activity (temperature ≥15°C, no rain, daylight)
    - Egg laying (temperature ≥10°C for new brood)
    - Effective nectar collection (sunlight hours, temperature)
    """

    def __init__(self,
                 location_name: str = "Maramures",
                 latitude: float = 47.66,  # Baia Mare latitude
                 altitude: int = 220,
                 start_date: Tuple[int, int] = (3, 1),
                 weather_seed: Optional[int] = None):
        """
        Initialize weather model for a location.

        Args:
            location_name: Name of location for reference
            latitude: Latitude in degrees (affects day length)
            altitude: Altitude in meters (affects temperature)
            start_date: Starting (month, day) tuple
            weather_seed: Random seed for reproducible weather (None = random)
        """
        self.location_name = location_name
        self.latitude = latitude
        self.altitude = altitude
        self.start_date = start_date
        self.weather_seed = weather_seed

        # Climate parameters for Maramures (continental climate)
        self.annual_avg_temp = 8.5  # °C average for the region
        self.temp_amplitude = 22.0  # Seasonal variation amplitude
        self.temp_daily_variation = 8.0  # Daily min/max spread

        # Altitude correction: -0.6°C per 100m
        self.altitude_correction = -(self.altitude / 100) * 0.6

        # Precipitation parameters
        self.annual_rainy_days = 120  # ~120 rainy days per year
        self.spring_rain_factor = 1.2  # More rain in spring
        self.summer_rain_factor = 1.3  # Summer thunderstorms
        self.fall_rain_factor = 1.1
        self.winter_rain_factor = 0.8

        # Initialize random state
        if weather_seed is not None:
            self.rng = np.random.RandomState(weather_seed)
        else:
            self.rng = np.random.RandomState()

    def _date_to_day_of_year(self, date: Tuple[int, int]) -> int:
        """Convert (month, day) to day of year (1-365)."""
        month, day = date
        days_before_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        return days_before_month[month - 1] + day

    def _calculate_day_length(self, day_of_year: int) -> float:
        """
        Calculate daylight hours for a given day of year.

        Uses simplified solar calculation based on latitude and day of year.

        Args:
            day_of_year: Day of year (1-365)

        Returns:
            Daylight hours (approximately 8-16 hours for Maramures latitude)
        """
        # Solar declination (simplified)
        declination = 23.45 * math.sin(math.radians((360 / 365.0) * (day_of_year - 81)))

        # Hour angle
        lat_rad = math.radians(self.latitude)
        dec_rad = math.radians(declination)

        cos_hour_angle = -math.tan(lat_rad) * math.tan(dec_rad)

        # Clamp to valid range
        cos_hour_angle = max(-1, min(1, cos_hour_angle))

        hour_angle = math.degrees(math.acos(cos_hour_angle))
        daylight_hours = (2.0 / 15.0) * hour_angle

        return daylight_hours

    def _calculate_useful_sunlight(self, day_of_year: int,
                                   cloud_cover: float = 0.3) -> float:
        """
        Calculate useful foraging hours considering cloud cover and bee behavior.

        Bees typically forage during middle hours of the day, avoiding
        early morning and late evening even when sun is up.

        Args:
            day_of_year: Day of year (1-365)
            cloud_cover: Cloud coverage factor (0-1), reduces useful hours

        Returns:
            Useful sunlight hours for foraging (typically 6-10 hours max)
        """
        total_daylight = self._calculate_day_length(day_of_year)

        # Bees forage primarily in middle 70% of daylight hours
        useful_hours = total_daylight * 0.7

        # Cloud cover reduces effective hours
        useful_hours *= (1.0 - cloud_cover * 0.4)

        # Cap at realistic maximum foraging window
        useful_hours = min(useful_hours, 10.0)

        return useful_hours

    def _calculate_temperature(self, day_of_year: int) -> Tuple[float, float, float]:
        """
        Calculate daily temperature (min, max, avg) for given day of year.

        Uses sinusoidal model with:
        - Peak summer temps (~Day 200, mid-July)
        - Minimum winter temps (~Day 15, mid-January)
        - Random daily variation
        - Altitude correction

        Args:
            day_of_year: Day of year (1-365)

        Returns:
            Tuple of (min_temp, max_temp, avg_temp) in Celsius
        """
        # Base seasonal temperature (sinusoidal)
        # Peak around day 200 (mid-July), minimum around day 15 (mid-January)
        seasonal_temp = self.annual_avg_temp + self.temp_amplitude * math.sin(
            math.radians((360 / 365.0) * (day_of_year - 105))
        )

        # Apply altitude correction
        seasonal_temp += self.altitude_correction

        # Add random daily variation (-2 to +2°C from seasonal average)
        daily_variation = self.rng.normal(0, 2.0)
        avg_temp = seasonal_temp + daily_variation

        # Calculate min/max with realistic daily spread
        daily_spread = self.temp_daily_variation + self.rng.normal(0, 1.5)
        min_temp = avg_temp - daily_spread / 2
        max_temp = avg_temp + daily_spread / 2

        return min_temp, max_temp, avg_temp

    def _calculate_precipitation(self, day_of_year: int) -> Tuple[bool, float]:
        """
        Determine if it rains on a given day and how much.

        Uses seasonal patterns:
        - More frequent in spring (Apr-May)
        - Summer thunderstorms (Jun-Aug)
        - Moderate in fall
        - Less in winter (often snow)

        Args:
            day_of_year: Day of year (1-365)

        Returns:
            Tuple of (is_rainy: bool, precipitation_mm: float)
        """
        # Determine season factor
        if 60 <= day_of_year < 152:  # Mar-May (spring)
            season_factor = self.spring_rain_factor
        elif 152 <= day_of_year < 244:  # Jun-Aug (summer)
            season_factor = self.summer_rain_factor
        elif 244 <= day_of_year < 335:  # Sep-Nov (fall)
            season_factor = self.fall_rain_factor
        else:  # Dec-Feb (winter)
            season_factor = self.winter_rain_factor

        # Base probability of rain on any given day
        base_rain_prob = (self.annual_rainy_days / 365.0) * season_factor

        # Determine if it rains
        is_rainy = self.rng.random() < base_rain_prob

        if is_rainy:
            # Amount of precipitation (exponential distribution)
            # Most days: light rain (2-10mm)
            # Some days: moderate rain (10-25mm)
            # Rare: heavy rain (25-50mm)
            precipitation = self.rng.exponential(8.0)
            precipitation = min(precipitation, 50.0)  # Cap at 50mm
        else:
            precipitation = 0.0

        return is_rainy, precipitation

    def _calculate_foraging_modifier(self, temp_avg: float, temp_max: float,
                                    is_rainy: bool, useful_sunlight: float) -> float:
        """
        Calculate foraging activity modifier (0.0-1.0).

        Foraging conditions depend on:
        - Temperature: Need ≥15°C (optimal 20-30°C)
        - Rain: Prevents foraging
        - Sunlight: More hours = more foraging

        Args:
            temp_avg: Average temperature (°C)
            temp_max: Maximum temperature (°C)
            is_rainy: Whether it's raining
            useful_sunlight: Useful foraging hours

        Returns:
            Foraging modifier (0.0-1.0)
        """
        # Rain prevents foraging
        if is_rainy:
            return 0.0

        # Temperature effect (bees need ≥15°C to forage effectively)
        if temp_max < 15.0:
            temp_modifier = 0.0
        elif temp_max < 18.0:
            # Gradual ramp-up 15-18°C (limited foraging)
            temp_modifier = (temp_max - 15.0) / 3.0 * 0.5
        elif temp_avg < 20.0:
            # Below 20°C average: reduced foraging
            temp_modifier = 0.5 + (temp_avg - 18.0) / 2.0 * 0.3
        elif temp_avg <= 30.0:
            # Optimal foraging range 20-30°C
            temp_modifier = 1.0
        else:
            # Too hot (>30°C): slightly reduced foraging
            temp_modifier = max(0.8, 1.0 - (temp_avg - 30.0) / 10.0 * 0.2)

        # Sunlight hours modifier (more hours = more foraging)
        sunlight_modifier = min(1.0, useful_sunlight / 10.0)

        # Combined effect
        foraging_modifier = temp_modifier * sunlight_modifier

        return max(0.0, min(1.0, foraging_modifier))

    def _calculate_brood_rearing_modifier(self, temp_avg: float, temp_min: float) -> float:
        """
        Calculate brood rearing modifier (0.0-1.0).

        Cold weather forces bees to focus on heating existing brood
        rather than starting new brood. Below 10°C, queen stops laying.

        Args:
            temp_avg: Average temperature (°C)
            temp_min: Minimum temperature (°C)

        Returns:
            Brood rearing modifier (0.0-1.0)
        """
        # Below 10°C average: brood heating mode, minimal/no new eggs
        if temp_avg < 10.0:
            return 0.0
        elif temp_avg < 12.0:
            # Gradual ramp-up 10-12°C
            return (temp_avg - 10.0) / 2.0 * 0.3
        elif temp_avg < 15.0:
            # 12-15°C: reduced egg laying
            return 0.3 + (temp_avg - 12.0) / 3.0 * 0.4
        elif temp_avg >= 15.0:
            # Above 15°C: normal brood rearing
            return 1.0

        return 1.0

    def generate_weather(self, num_days: int) -> pd.DataFrame:
        """
        Generate weather data for specified number of days.

        Args:
            num_days: Number of days to generate weather for

        Returns:
            DataFrame with columns:
            - day: Simulation day (0-indexed)
            - day_of_year: Calendar day of year (1-365)
            - date_string: Human-readable date
            - temp_min: Minimum temperature (°C)
            - temp_max: Maximum temperature (°C)
            - temp_avg: Average temperature (°C)
            - is_rainy: Boolean indicating rain
            - precipitation_mm: Precipitation amount
            - daylight_hours: Total daylight hours
            - useful_sunlight_hours: Effective foraging hours
            - foraging_modifier: Foraging activity (0-1)
            - brood_rearing_modifier: Egg laying activity (0-1)
        """
        # Calculate starting day of year
        start_doy = self._date_to_day_of_year(self.start_date)

        # Initialize data storage
        data = {
            'day': [],
            'day_of_year': [],
            'date_string': [],
            'temp_min': [],
            'temp_max': [],
            'temp_avg': [],
            'is_rainy': [],
            'precipitation_mm': [],
            'daylight_hours': [],
            'useful_sunlight_hours': [],
            'foraging_modifier': [],
            'brood_rearing_modifier': []
        }

        # Generate weather for each day
        for day in range(num_days):
            current_doy = ((start_doy + day - 1) % 365) + 1

            # Calculate weather components
            min_temp, max_temp, avg_temp = self._calculate_temperature(current_doy)
            is_rainy, precip = self._calculate_precipitation(current_doy)
            daylight = self._calculate_day_length(current_doy)

            # Cloud cover estimate (higher when rainy)
            cloud_cover = 0.7 if is_rainy else self.rng.uniform(0.1, 0.4)
            useful_sun = self._calculate_useful_sunlight(current_doy, cloud_cover)

            # Calculate modifiers
            foraging_mod = self._calculate_foraging_modifier(
                avg_temp, max_temp, is_rainy, useful_sun
            )
            brood_mod = self._calculate_brood_rearing_modifier(avg_temp, min_temp)

            # Date string (simple conversion)
            date_str = self._day_of_year_to_date_string(current_doy)

            # Store data
            data['day'].append(day)
            data['day_of_year'].append(current_doy)
            data['date_string'].append(date_str)
            data['temp_min'].append(round(min_temp, 1))
            data['temp_max'].append(round(max_temp, 1))
            data['temp_avg'].append(round(avg_temp, 1))
            data['is_rainy'].append(is_rainy)
            data['precipitation_mm'].append(round(precip, 1))
            data['daylight_hours'].append(round(daylight, 1))
            data['useful_sunlight_hours'].append(round(useful_sun, 1))
            data['foraging_modifier'].append(round(foraging_mod, 3))
            data['brood_rearing_modifier'].append(round(brood_mod, 3))

        # Create DataFrame
        df = pd.DataFrame(data)
        df.set_index('day', inplace=True)

        return df

    def _day_of_year_to_date_string(self, day_of_year: int) -> str:
        """Convert day of year to 'Mon DD' string format."""
        days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        month = 0
        day = day_of_year

        for i, days in enumerate(days_in_months):
            if day <= days:
                month = i
                break
            day -= days

        return f"{month_names[month]} {day:02d}"

    def get_weather_summary(self, weather_df: pd.DataFrame) -> dict:
        """
        Generate summary statistics from weather DataFrame.

        Args:
            weather_df: Weather DataFrame from generate_weather()

        Returns:
            Dictionary with summary statistics
        """
        return {
            'location': self.location_name,
            'days_simulated': len(weather_df),
            'temp_avg': weather_df['temp_avg'].mean(),
            'temp_min_overall': weather_df['temp_min'].min(),
            'temp_max_overall': weather_df['temp_max'].max(),
            'rainy_days': weather_df['is_rainy'].sum(),
            'total_precipitation_mm': weather_df['precipitation_mm'].sum(),
            'avg_daylight_hours': weather_df['daylight_hours'].mean(),
            'avg_foraging_hours': weather_df['useful_sunlight_hours'].mean(),
            'avg_foraging_modifier': weather_df['foraging_modifier'].mean(),
            'days_no_foraging': (weather_df['foraging_modifier'] == 0).sum(),
            'days_limited_foraging': ((weather_df['foraging_modifier'] > 0) &
                                     (weather_df['foraging_modifier'] < 0.5)).sum(),
            'days_good_foraging': (weather_df['foraging_modifier'] >= 0.5).sum(),
            'avg_brood_modifier': weather_df['brood_rearing_modifier'].mean(),
            'days_no_brood': (weather_df['brood_rearing_modifier'] == 0).sum()
        }

    def to_dataframes(self, num_days: int) -> dict:
        """
        Generate weather data in dict format matching simulator API.

        Args:
            num_days: Number of days to generate

        Returns:
            Dictionary with:
            - 'weather': DataFrame with all weather data
            - 'metadata': Dictionary with configuration
        """
        weather_df = self.generate_weather(num_days)
        summary = self.get_weather_summary(weather_df)

        return {
            'weather': weather_df,
            'metadata': {
                'model_type': 'WeatherModel',
                'location': self.location_name,
                'latitude': self.latitude,
                'altitude': self.altitude,
                'start_date': self.start_date,
                'weather_seed': self.weather_seed,
                'summary': summary
            }
        }


# Predefined weather models for common locations
def create_baia_mare_weather(start_date: Tuple[int, int] = (3, 1),
                             seed: Optional[int] = None) -> WeatherModel:
    """Create weather model for Baia Mare (220m altitude)."""
    return WeatherModel(
        location_name="Baia Mare",
        latitude=47.66,
        altitude=220,
        start_date=start_date,
        weather_seed=seed
    )


def create_chiuzbaia_weather(start_date: Tuple[int, int] = (3, 1),
                             seed: Optional[int] = None) -> WeatherModel:
    """Create weather model for Chiuzbaia (575m altitude)."""
    return WeatherModel(
        location_name="Chiuzbaia",
        latitude=47.60,
        altitude=575,  # Higher altitude = cooler temperatures
        start_date=start_date,
        weather_seed=seed
    )


if __name__ == "__main__":
    # Example usage and demonstration
    print("=" * 80)
    print("WEATHER MODEL DEMONSTRATION")
    print("=" * 80)

    # Create weather model for Baia Mare
    weather = create_baia_mare_weather(start_date=(3, 1), seed=42)

    # Generate 90 days of weather (March, April, May)
    print("\nGenerating 90 days of spring weather for Baia Mare...")
    results = weather.to_dataframes(num_days=90)

    weather_df = results['weather']
    summary = results['metadata']['summary']

    # Print summary
    print("\n=== Weather Summary ===")
    print(f"Location: {summary['location']}")
    print(f"Days simulated: {summary['days_simulated']}")
    print(f"Average temperature: {summary['temp_avg']:.1f}°C")
    print(f"Temperature range: {summary['temp_min_overall']:.1f}°C to {summary['temp_max_overall']:.1f}°C")
    print(f"Rainy days: {summary['rainy_days']} ({summary['rainy_days']/summary['days_simulated']*100:.1f}%)")
    print(f"Total precipitation: {summary['total_precipitation_mm']:.0f} mm")
    print(f"Average daylight: {summary['avg_daylight_hours']:.1f} hours")
    print(f"Average foraging hours: {summary['avg_foraging_hours']:.1f} hours")
    print(f"\nForaging conditions:")
    print(f"  No foraging: {summary['days_no_foraging']} days")
    print(f"  Limited foraging: {summary['days_limited_foraging']} days")
    print(f"  Good foraging: {summary['days_good_foraging']} days")
    print(f"\nBrood rearing:")
    print(f"  Days too cold for new brood: {summary['days_no_brood']} days")
    print(f"  Average brood modifier: {summary['avg_brood_modifier']:.3f}")

    # Print sample days
    print("\n=== Sample Days ===")
    print(weather_df.head(10).to_string())

    print("\n" + "=" * 80)
    print("Weather DataFrame ready for integration with bee simulator!")
    print("=" * 80)
