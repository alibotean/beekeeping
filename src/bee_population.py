import numpy as np
import matplotlib.pyplot as plt
from collections import deque

class BeeHiveSimulator:
    """
    Simulates bee population dynamics in a Dadant hive system.
    
    The simulation tracks:
    - Adult bee population (foragers, nurses, house bees)
    - Developing brood at various stages (eggs, larvae, pupae)
    - Queen status and egg-laying capacity
    - Frame capacity constraints
    """
    
    def __init__(self, 
                 total_frames=10,
                 initial_brood_frames=6,
                 attrition_rate=300,
                 egg_laying_rate=1100,
                 worker_development_days=21,
                 queen_development_days=16,
                 queen_mating_days=10,
                 cells_per_frame=7000):
        
        # Hive configuration
        self.total_frames = total_frames
        self.brood_frames = initial_brood_frames
        self.cells_per_frame = cells_per_frame
        
        # Population rates
        self.attrition_rate = attrition_rate  # Adult bees dying per day
        self.egg_laying_rate = egg_laying_rate  # Eggs laid per day by queen
        
        # Development timelines
        self.worker_dev_days = worker_development_days
        self.queen_dev_days = queen_development_days
        self.queen_mating_days = queen_mating_days
        
        # Population tracking
        # We use a deque to track when each cohort of bees will emerge
        # Index 0 = today's eggs, index 20 = bees emerging tomorrow
        self.developing_brood = deque([0] * worker_development_days, 
                                       maxlen=worker_development_days)
        
        # Initial adult population (estimate based on brood frames)
        # Rule of thumb: 1 frame of brood = ~3000-4000 adult bees needed to care for it
        self.adult_bees = initial_brood_frames * 3500
        
        # Queen status
        self.has_laying_queen = True
        self.queen_development_day = None  # Tracks queen development if needed
        
        # History for plotting
        self.history = {
            'day': [],
            'adult_bees': [],
            'total_brood': [],
            'eggs_laid': [],
            'bees_emerged': [],
            'bees_died': [],
            'eggs': [],
            'larvae': [],
            'pupae': [],
            'brood_occupancy_pct': []
        }
    
    def get_max_brood_capacity(self):
        """Calculate maximum number of cells available for brood"""
        # Each brood frame can hold ~7000 cells
        # Typically, not all cells are used (some for pollen, nectar)
        # We assume 85% of cells available for brood
        return int(self.brood_frames * self.cells_per_frame * 0.85)
    
    def get_current_brood_count(self):
        """Count all developing brood across all stages"""
        return sum(self.developing_brood)

    def get_brood_by_stage(self):
        """
        Get brood counts by developmental stage:
        - Eggs: days 0-2 (days 1-3 of development)
        - Larvae: days 3-7 (days 4-8 of development)
        - Pupae: days 8-20 (days 9-21 of development)

        Returns: tuple of (eggs, larvae, pupae)
        """
        brood_list = list(self.developing_brood)

        # Days 0-2 are eggs (first 3 days)
        eggs = sum(brood_list[0:3])

        # Days 3-7 are larvae (days 4-8)
        larvae = sum(brood_list[3:8])

        # Days 8-20 are pupae (days 9-21)
        pupae = sum(brood_list[8:])

        return eggs, larvae, pupae

    def get_brood_occupancy_percentage(self):
        """Calculate what percentage of available brood cells are occupied"""
        current_brood = self.get_current_brood_count()
        max_capacity = self.get_max_brood_capacity()

        if max_capacity == 0:
            return 0.0

        return (current_brood / max_capacity) * 100.0

    def add_frames(self, num_frames):
        """Add frames to the brood chamber (simulates hive expansion)"""
        import json

        old_count = self.brood_frames
        self.brood_frames = min(self.brood_frames + num_frames, self.total_frames)
        actual_added = self.brood_frames - old_count

        # Record event (no print)
        if hasattr(self, 'events'):
            current_day = len(self.history['day']) if self.history['day'] else 0
            self.events.append({
                'day': current_day,
                'event_type': 'frame_addition',
                'description': f'Added {actual_added} frame(s). Total: {self.brood_frames}',
                'details': json.dumps({
                    'requested': num_frames,
                    'added': actual_added,
                    'new_total': self.brood_frames
                })
            })
    
    def lose_queen(self, day):
        """Simulate queen loss - colony becomes queenless"""
        import json

        self.has_laying_queen = False
        self.queen_development_day = 0  # Start counting days for emergency queen cells

        # Record event (no print)
        if hasattr(self, 'events'):
            self.events.append({
                'day': day,
                'event_type': 'queen_loss',
                'description': 'QUEEN LOST - Colony is now queenless',
                'details': json.dumps({'emergency_cells_started': True})
            })
    
    def simulate_day(self, day):
        """Simulate one day in the hive"""
        
        # Track daily events
        eggs_laid_today = 0
        bees_emerged_today = 0
        bees_died_today = 0
        
        # 1. ADULT BEE MORTALITY
        # Bees die from old age, disease, predation, foraging losses
        bees_died_today = min(self.attrition_rate, self.adult_bees)
        self.adult_bees -= bees_died_today
        
        # 2. NEW BEES EMERGING
        # Bees that were eggs 21 days ago now emerge as adults
        bees_emerged_today = self.developing_brood[-1]
        self.adult_bees += bees_emerged_today
        
        # 3. QUEEN EGG LAYING
        if self.has_laying_queen:
            # Check capacity: queen won't lay if there's no space
            current_brood = self.get_current_brood_count()
            max_capacity = self.get_max_brood_capacity()
            available_space = max_capacity - current_brood
            
            # Queen lays eggs up to her capacity or available space
            eggs_laid_today = min(self.egg_laying_rate, available_space)
            
            # Add eggs to the brood pipeline (they'll emerge in 21 days)
            self.developing_brood.appendleft(eggs_laid_today)
        else:
            # No laying queen - no new eggs
            self.developing_brood.appendleft(0)
        
        # 4. QUEEN DEVELOPMENT (if colony is queenless)
        # This models emergency queen rearing or queen replacement
        if not self.has_laying_queen and self.queen_development_day is not None:
            self.queen_development_day += 1
            
            # Virgin queen emerges after 16 days
            if self.queen_development_day == self.queen_dev_days:
                # Record event (no print)
                if hasattr(self, 'events'):
                    import json
                    self.events.append({
                        'day': day,
                        'event_type': 'queen_emerged',
                        'description': 'Virgin queen emerged',
                        'details': json.dumps({'development_day': self.queen_development_day})
                    })

            # Virgin queen mates and starts laying after additional 10 days
            elif self.queen_development_day == self.queen_dev_days + self.queen_mating_days:
                self.has_laying_queen = True
                self.queen_development_day = None
                # Record event (no print)
                if hasattr(self, 'events'):
                    import json
                    self.events.append({
                        'day': day,
                        'event_type': 'queen_mated',
                        'description': 'Queen mated and started laying eggs',
                        'details': json.dumps({'started_laying': True})
                    })
        
        # 5. RECORD HISTORY
        eggs, larvae, pupae = self.get_brood_by_stage()
        self.history['day'].append(day)
        self.history['adult_bees'].append(self.adult_bees)
        self.history['total_brood'].append(self.get_current_brood_count())
        self.history['eggs_laid'].append(eggs_laid_today)
        self.history['bees_emerged'].append(bees_emerged_today)
        self.history['bees_died'].append(bees_died_today)
        self.history['eggs'].append(eggs)
        self.history['larvae'].append(larvae)
        self.history['pupae'].append(pupae)
        self.history['brood_occupancy_pct'].append(self.get_brood_occupancy_percentage())
    
    def run_simulation(self, num_days, frames_to_add=None, queen_loss_day=None):
        """
        Run the simulation for specified number of days.

        Args:
            num_days: Number of days to simulate
            frames_to_add: dict mapping day number to number of frames to add
                           e.g., {1: 2, 10: 1, 20: 1}
            queen_loss_day: day on which the queen is lost (None = no queen loss)

        Returns:
            self (for method chaining)
        """
        if frames_to_add is None:
            frames_to_add = {}

        # Store parameters for metadata
        self._simulation_params = {
            'num_days': num_days,
            'frames_to_add': frames_to_add,
            'queen_loss_day': queen_loss_day
        }

        # Initialize events tracking
        if not hasattr(self, 'events'):
            self.events = []

        # Store initial state for metadata
        if not hasattr(self, '_initial_adult_bees'):
            self._initial_adult_bees = self.adult_bees
            self._initial_brood_frames = self.brood_frames
            self._initial_has_laying_queen = self.has_laying_queen

        # Main simulation loop
        for day in range(num_days):
            # Check if we should add frames on this day
            if day in frames_to_add:
                self.add_frames(frames_to_add[day])

            # Check if queen is lost on this day
            if queen_loss_day is not None and day == queen_loss_day:
                self.lose_queen(day)

            # Simulate the day
            self.simulate_day(day)

        return self  # Allow method chaining

    def to_dataframes(self):
        """
        Convert simulation results to structured pandas DataFrames.

        Returns:
            Dictionary containing:
            - 'population': DataFrame with adult_bees, brood stages, occupancy
            - 'dynamics': DataFrame with daily changes and rates
            - 'events': DataFrame with discrete events
            - 'metadata': Dict with configuration and parameters
        """
        import pandas as pd
        import json

        # Handle empty simulation
        if not self.history['day']:
            return {
                'population': pd.DataFrame(columns=['day', 'adult_bees', 'total_brood', 'eggs', 'larvae', 'pupae', 'brood_occupancy_pct']),
                'dynamics': pd.DataFrame(columns=['day', 'eggs_laid', 'bees_emerged', 'bees_died', 'net_change', 'egg_laying_rate', 'attrition_rate']),
                'events': pd.DataFrame(columns=['day', 'event_type', 'description', 'details']),
                'metadata': self._build_metadata()
            }

        # Population DataFrame
        population = pd.DataFrame({
            'day': self.history['day'],
            'adult_bees': self.history['adult_bees'],
            'total_brood': self.history['total_brood'],
            'eggs': self.history['eggs'],
            'larvae': self.history['larvae'],
            'pupae': self.history['pupae'],
            'brood_occupancy_pct': self.history['brood_occupancy_pct']
        }).set_index('day')

        # Dynamics DataFrame
        dynamics = pd.DataFrame({
            'day': self.history['day'],
            'eggs_laid': self.history['eggs_laid'],
            'bees_emerged': self.history['bees_emerged'],
            'bees_died': self.history['bees_died'],
            'egg_laying_rate': [self.egg_laying_rate] * len(self.history['day']),
            'attrition_rate': [self.attrition_rate] * len(self.history['day'])
        }).set_index('day')
        dynamics['net_change'] = dynamics['bees_emerged'] - dynamics['bees_died']

        # Events DataFrame
        events = pd.DataFrame(self.events if hasattr(self, 'events') else [])

        return {
            'population': population,
            'dynamics': dynamics,
            'events': events,
            'metadata': self._build_metadata()
        }

    def _build_metadata(self):
        """Build metadata dictionary from instance variables."""
        return {
            'simulator_type': self.__class__.__name__,
            'simulation_config': {
                'total_frames': self.total_frames,
                'initial_brood_frames': getattr(self, '_initial_brood_frames', self.brood_frames),
                'cells_per_frame': self.cells_per_frame,
                'worker_development_days': self.worker_dev_days,
                'queen_development_days': self.queen_dev_days,
                'queen_mating_days': self.queen_mating_days,
            },
            'base_rates': {
                'egg_laying_rate': self.egg_laying_rate,
                'attrition_rate': self.attrition_rate,
            },
            'initial_state': {
                'adult_bees': getattr(self, '_initial_adult_bees', self.adult_bees),
                'has_laying_queen': getattr(self, '_initial_has_laying_queen', self.has_laying_queen),
            },
            'simulation_parameters': getattr(self, '_simulation_params', {})
        }


# Example usage: Running a typical simulation scenario
if __name__ == "__main__":
    print("=" * 60)
    print("SCENARIO 1: Normal Colony Development")
    print("=" * 60)
    
    # Create a simulator with default parameters
    sim1 = BeeHiveSimulator(
        total_frames=10,           # Total frame capacity in brood chamber
        initial_brood_frames=6,    # Starting with 6 frames of brood
        attrition_rate=1000,       # 1000 bees die per day
        egg_laying_rate=1100,      # Queen lays 1100 eggs per day
        worker_development_days=21, # 21 days from egg to adult
        cells_per_frame=7000       # Dadant frame capacity
    )
    
    # Define when to add frames (day: number_of_frames)
    frame_additions = {
        1: 2,   # Add 2 frames on day 1
        10: 1,  # Add 1 frame on day 10
        20: 1   # Add 1 frame on day 20
    }
    
    # Run simulation for 60 days - NO queen loss
    sim1.run_simulation(num_days=60, frames_to_add=frame_additions)
    sim1.plot_results()
    
    print("\n" + "=" * 60)
    print("SCENARIO 2: Queen Loss on Day 15")
    print("=" * 60)
    
    # Create another simulator to compare with queen loss
    sim2 = BeeHiveSimulator(
        total_frames=10,
        initial_brood_frames=6,
        attrition_rate=1000,
        egg_laying_rate=1100,
        worker_development_days=21,
        cells_per_frame=7000
    )
    
    # Run simulation with queen loss on day 15
    # This models scenarios like: queen killed during inspection, 
    # failing queen, supersedure, or lost during mating flight
    sim2.run_simulation(
        num_days=80, 
        frames_to_add=frame_additions,
        queen_loss_day=15  # Queen is lost on day 15
    )
    sim2.plot_results()
