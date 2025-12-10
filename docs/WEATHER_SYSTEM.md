# Weather System Documentation

## Overview

The Weather System adds realistic environmental conditions to bee colony simulations, modeling the impact of temperature, precipitation, and sunlight on bee behavior.

## Key Concepts

### Weather Thresholds

| Condition | Threshold | Effect |
|-----------|-----------|--------|
| **Foraging Temperature** | ≥15°C | Bees can forage effectively |
| **Brood Rearing Temperature** | ≥10°C | Queen lays new eggs |
| **Optimal Foraging** | 20-30°C | Peak foraging activity |
| **Maximum Sunlight** | 10 hours | Effective foraging window |
| **Rain** | Any amount | Prevents foraging completely |

### Temperature Effects

```
Temperature    | Foraging | Brood Rearing | Effect
---------------|----------|---------------|---------------------------
< 10°C         | 0%       | 0%            | Survival mode - heat cluster
10-12°C        | 0%       | 0-30%         | Minimal activity
12-15°C        | 0%       | 30-70%        | Reduced egg laying
15-18°C        | 0-50%    | 70-100%       | Limited foraging begins
18-20°C        | 50-80%   | 100%          | Increasing activity
20-30°C        | 100%     | 100%          | Optimal conditions
> 30°C         | 80%      | 100%          | Slight reduction (heat stress)
```

## WeatherModel Class

### Initialization

```python
from weather_model import WeatherModel, create_baia_mare_weather

# Create custom weather model
weather = WeatherModel(
    location_name="Baia Mare",
    latitude=47.66,           # Affects day length
    altitude=220,             # Affects temperature (-0.6°C per 100m)
    start_date=(3, 1),        # March 1st
    weather_seed=42           # For reproducible weather (optional)
)

# Or use predefined locations
weather = create_baia_mare_weather(start_date=(3, 1), seed=42)
weather = create_chiuzbaia_weather(start_date=(3, 1), seed=42)
```

### Generate Weather Data

```python
# Generate 270 days of weather
results = weather.to_dataframes(num_days=270)

weather_df = results['weather']
metadata = results['metadata']

# Access weather data
print(weather_df.head())
```

### Weather DataFrame Structure

```
Columns:
- day: Simulation day (0-indexed)
- day_of_year: Calendar day (1-365)
- date_string: Human-readable date ('Mar 01')
- temp_min: Minimum temperature (°C)
- temp_max: Maximum temperature (°C)
- temp_avg: Average temperature (°C)
- is_rainy: Boolean indicating rain
- precipitation_mm: Rain amount (mm)
- daylight_hours: Total daylight (astronomical)
- useful_sunlight_hours: Effective foraging hours (4-10)
- foraging_modifier: Foraging activity level (0.0-1.0)
- brood_rearing_modifier: Egg laying level (0.0-1.0)
```

## Integration with Bee Simulator

### Modifier Hierarchy

Weather modifiers multiply with calendar modifiers:

```
Final Rate = Base Rate × Calendar Modifier × Weather Modifier

Example:
Base egg laying: 1100 eggs/day
Calendar (Acacia flow): ×1.4
Weather (cold, rainy): ×0.3
Final: 1100 × 1.4 × 0.3 = 462 eggs/day
```

### Integration Approaches

#### 1. Post-Processing (Current Example)

```python
from seasonal_bee_simulator import SeasonalBeeSimulator
from weather_model import create_baia_mare_weather

# Generate weather
weather = create_baia_mare_weather(start_date=(3, 1), seed=42)
weather_data = weather.to_dataframes(num_days=270)

# Run simulation
sim = SeasonalBeeSimulator(...)
for day in range(270):
    # Apply weather modifiers
    weather_row = weather_data['weather'].iloc[day]

    # Adjust egg laying by brood modifier
    sim.base_egg_laying_rate = int(1100 * weather_row['brood_rearing_modifier'])

    # Adjust attrition in bad weather
    if weather_row['foraging_modifier'] < 0.3:
        sim.base_attrition_rate = int(600 * 1.1)  # 10% increase

    # Simulate day
    sim.simulate_day(day)

    # Adjust honey production by foraging modifier
    current_honey = sim.history['daily_honey_production'][-1]
    adjusted_honey = current_honey * weather_row['foraging_modifier']
    sim.history['daily_honey_production'][-1] = adjusted_honey

results = sim.to_dataframes()
```

#### 2. Native Integration (Recommended for Production)

Modify `SeasonalBeeSimulator.__init__`:

```python
def __init__(self, calendar, weather_model=None, **kwargs):
    self.weather_model = weather_model

    if weather_model:
        self.weather_data = weather_model.generate_weather(num_days=365)
```

Modify `SeasonalBeeSimulator.simulate_day`:

```python
def simulate_day(self, day):
    # Get calendar factors
    calendar_factors = self.calendar.get_daily_factors(self.current_day_of_year)

    # Get weather factors
    if self.weather_model:
        weather_row = self.weather_data.iloc[day % len(self.weather_data)]
        weather_foraging = weather_row['foraging_modifier']
        weather_brood = weather_row['brood_rearing_modifier']
    else:
        weather_foraging = 1.0
        weather_brood = 1.0

    # Apply combined modifiers
    effective_egg_rate = int(
        self.base_egg_laying_rate *
        calendar_factors['egg_rate_modifier'] *
        weather_brood
    )

    # Continue with simulation...
```

## Realistic Weather Patterns

### Maramures Climate (Continental)

```
Month       | Avg Temp | Rainy Days | Foraging Days
------------|----------|------------|---------------
January     | -3°C     | 8          | 0
February    | -1°C     | 7          | 0-2
March       | 5°C      | 9          | 5-10
April       | 11°C     | 11         | 12-18
May         | 16°C     | 13         | 18-25
June        | 19°C     | 14         | 20-26
July        | 21°C     | 12         | 24-28
August      | 20°C     | 11         | 24-28
September   | 16°C     | 9          | 18-22
October     | 11°C     | 9          | 10-15
November    | 4°C      | 10         | 2-5
December    | -1°C     | 9          | 0
```

### Weather Variability

The model includes realistic day-to-day variation:

- **Temperature**: ±2°C daily deviation from seasonal average
- **Daily spread**: 8±1.5°C between min and max
- **Rain probability**: Seasonal patterns with randomness
- **Cloud cover**: Higher on rainy days (affects sunlight)

### Altitude Effects

Temperature decreases with altitude:
- **Baia Mare (220m)**: Base temperature
- **Chiuzbaia (575m)**: -2.1°C adjustment (-0.6°C per 100m)

This delays spring by ~10-15 days at higher elevations.

## Example Scenarios

### Scenario 1: Weather Impact Analysis

```python
from weather_integration_example import scenario_weather_impact_comparison

# Compare ideal vs realistic conditions
scenario_weather_impact_comparison()
```

This demonstrates:
- Population reduction due to weather (typically 10-20%)
- Honey production loss (typically 15-30%)
- Impact of cold springs vs warm springs
- Effect of rainy periods during major flows

### Scenario 2: Spring Buildup Under Poor Weather

```python
weather = create_baia_mare_weather(start_date=(3, 1), seed=101)  # Cold spring
results = weather.to_dataframes(num_days=90)

# Check early spring conditions
march_weather = results['weather'][results['weather']['day_of_year'] < 91]
avg_foraging = march_weather['foraging_modifier'].mean()

print(f"March foraging conditions: {avg_foraging:.1%}")
# Typical: 20-40% (many days too cold)
```

### Scenario 3: Summer Dearth with Rain

During summer dearth (July-August), rain prevents foraging on remaining flows:

```python
# Generate July-August weather
weather = create_baia_mare_weather(start_date=(7, 1), seed=42)
summer_data = weather.to_dataframes(num_days=60)

rainy_days = summer_data['weather']['is_rainy'].sum()
print(f"Rainy days in July-Aug: {rainy_days}/60")
# Typical: 12-15 rainy days = 20-25% loss of foraging time
```

## Weather Statistics

### Key Metrics

```python
from weather_model import WeatherModel

weather = WeatherModel(...)
weather_df = weather.generate_weather(num_days=270)
summary = weather.get_weather_summary(weather_df)

print(f"Average temperature: {summary['temp_avg']:.1f}°C")
print(f"Rainy days: {summary['rainy_days']}")
print(f"Days with good foraging: {summary['days_good_foraging']}")
print(f"Days too cold for brood: {summary['days_no_brood']}")
```

### Typical Full Season (March-November)

For Baia Mare, 270 days starting March 1:

```
Average temperature: 13-15°C
Temperature range: -10°C to 32°C
Rainy days: 90-110 (33-40%)
Total precipitation: 450-550mm

Foraging conditions:
- No foraging: 80-100 days (30-37%)
- Limited foraging: 60-80 days (22-30%)
- Good foraging: 90-120 days (33-45%)

Brood rearing:
- Too cold for new brood: 60-80 days (22-30%)
- Average brood modifier: 0.65-0.75
```

## Best Practices

### 1. Use Consistent Seeds for Comparisons

```python
# Compare strategies under same weather
weather_seed = 42

sim1 = run_strategy_A(weather_seed=weather_seed)
sim2 = run_strategy_B(weather_seed=weather_seed)
```

### 2. Run Multiple Weather Years

```python
# Average results over 5 different weather patterns
results = []
for seed in range(5):
    weather = create_baia_mare_weather(start_date=(3, 1), seed=seed)
    result = run_simulation_with_weather(weather)
    results.append(result)

avg_final_population = np.mean([r['final_pop'] for r in results])
```

### 3. Consider Critical Periods

Focus weather analysis on critical periods:
- **Early spring (March-April)**: Cold delays buildup
- **Acacia flow (May 1-15)**: Rain = lost honey crop
- **Summer dearth (July-Aug)**: Stress period
- **Fall preparation (Sept-Oct)**: Build winter bees

### 4. Validate Weather Patterns

```python
# Ensure weather is realistic
weather_df = weather.generate_weather(num_days=365)

# Check annual statistics
annual_avg_temp = weather_df['temp_avg'].mean()
assert 7 < annual_avg_temp < 10, "Unrealistic annual average"

annual_rainy_days = weather_df['is_rainy'].sum()
assert 100 < annual_rainy_days < 140, "Unrealistic precipitation"
```

## Future Enhancements

### Planned Features

1. **Multi-year weather cycles**
   - Warm years vs cold years
   - Drought years
   - El Niño/La Niña patterns

2. **Extreme weather events**
   - Late spring frost (kills blooms)
   - Heat waves (stops foraging)
   - Extended rain periods (starvation risk)

3. **Historical weather data integration**
   - Import actual weather records
   - Replay specific years (e.g., "the cold spring of 2021")

4. **Microclimate modeling**
   - Hive location effects (sun exposure, wind protection)
   - Urban heat island effects
   - Valley vs hillside temperature differences

### Integration TODO

For full production integration:

```python
# TODO: Add to SeasonalBeeSimulator
class SeasonalBeeSimulator(BeeHiveSimulator):
    def __init__(self, calendar, weather_model=None, **kwargs):
        self.weather_model = weather_model

        # Initialize weather history tracking
        if weather_model:
            self.history['weather_temp'] = []
            self.history['weather_foraging'] = []
            self.history['weather_brood'] = []
            self.history['is_rainy'] = []

    def simulate_day(self, day):
        # Apply weather modifiers (shown above)
        pass

    def to_dataframes(self):
        results = super().to_dataframes()

        # Add weather DataFrame if available
        if self.weather_model:
            results['weather'] = pd.DataFrame({
                'day': self.history['day'],
                'temp_avg': self.history['weather_temp'],
                'foraging_modifier': self.history['weather_foraging'],
                'brood_modifier': self.history['weather_brood'],
                'is_rainy': self.history['is_rainy']
            }).set_index('day')

        return results
```

## References

- Beekeeping temperature thresholds: Free & Raby (1975)
- Continental climate modeling: Maramures meteorological data
- Bee foraging behavior: Winston (1987) "The Biology of the Honey Bee"
- Day length calculations: NOAA solar calculator

## Example Output

```
=== Weather Summary ===
Location: Baia Mare
Days simulated: 270
Average temperature: 14.2°C
Temperature range: -8.3°C to 31.4°C
Rainy days: 98 (36.3%)
Total precipitation: 487 mm
Average daylight: 13.8 hours
Average foraging hours: 8.2 hours

Foraging conditions:
  No foraging: 94 days (34.8%)
  Limited foraging: 68 days (25.2%)
  Good foraging: 108 days (40.0%)

Brood rearing:
  Days too cold for new brood: 71 days (26.3%)
  Average brood modifier: 0.689
```
