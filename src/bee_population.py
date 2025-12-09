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
        self.brood_frames = min(self.brood_frames + num_frames, 
                                 self.total_frames)
        print(f"  Added {num_frames} frame(s). Total brood frames: {self.brood_frames}")
    
    def lose_queen(self, day):
        """Simulate queen loss - colony becomes queenless"""
        self.has_laying_queen = False
        self.queen_development_day = 0  # Start counting days for emergency queen cells
        print(f"  Day {day}: QUEEN LOST - Colony is now queenless")
        print(f"  Emergency queen cells being started from young larvae")
    
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
                print(f"  Day {day}: Virgin queen emerged")
            
            # Virgin queen mates and starts laying after additional 10 days
            elif self.queen_development_day == self.queen_dev_days + self.queen_mating_days:
                self.has_laying_queen = True
                self.queen_development_day = None
                print(f"  Day {day}: Queen mated and started laying eggs")
        
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
        Run the simulation for specified number of days
        
        frames_to_add: dict mapping day number to number of frames to add
                       e.g., {1: 2, 10: 1, 20: 1}
        queen_loss_day: day on which the queen is lost (None = no queen loss)
        """
        if frames_to_add is None:
            frames_to_add = {}
        
        print(f"\n=== Starting Bee Population Simulation ===")
        print(f"Initial adult bees: {self.adult_bees:,}")
        print(f"Initial brood frames: {self.brood_frames}")
        print(f"Egg laying rate: {self.egg_laying_rate} eggs/day")
        print(f"Attrition rate: {self.attrition_rate} bees/day")
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
            
            # Print status every 10 days
            if day % 10 == 0:
                eggs, larvae, pupae = self.get_brood_by_stage()
                occupancy = self.get_brood_occupancy_percentage()
                print(f"Day {day:3d}: Adult bees: {self.adult_bees:6,}, "
                      f"Brood: {self.get_current_brood_count():6,} "
                      f"(Eggs: {eggs:5,}, Larvae: {larvae:5,}, Pupae: {pupae:5,}), "
                      f"Occupancy: {occupancy:5.1f}%")
        
        print(f"\n=== Simulation Complete ===")
        print(f"Final adult population: {self.adult_bees:,}")
        print(f"Final brood count: {self.get_current_brood_count():,}")
    
    def plot_results(self):
        """Create visualizations of the simulation results"""

        fig, axes = plt.subplots(3, 2, figsize=(14, 15))
        fig.suptitle('Bee Colony Population Dynamics', fontsize=16, fontweight='bold')

        days = self.history['day']

        # Plot 1: Adult bee population over time
        ax1 = axes[0, 0]
        ax1.plot(days, self.history['adult_bees'], 'b-', linewidth=2)
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Adult Bees')
        ax1.set_title('Adult Bee Population')
        ax1.grid(True, alpha=0.3)
        ax1.fill_between(days, self.history['adult_bees'], alpha=0.3)

        # Plot 2: Brood population over time
        ax2 = axes[0, 1]
        ax2.plot(days, self.history['total_brood'], 'g-', linewidth=2)
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Developing Brood')
        ax2.set_title('Total Brood (Eggs, Larvae, Pupae)')
        ax2.grid(True, alpha=0.3)
        ax2.fill_between(days, self.history['total_brood'], alpha=0.3, color='green')

        # Plot 3: Daily egg laying and bee emergence
        ax3 = axes[1, 0]
        ax3.plot(days, self.history['eggs_laid'], 'orange', linewidth=2, label='Eggs Laid')
        ax3.plot(days, self.history['bees_emerged'], 'purple', linewidth=2, label='Bees Emerged')
        ax3.set_xlabel('Days')
        ax3.set_ylabel('Number of Bees')
        ax3.set_title('Daily Egg Laying vs Bee Emergence')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

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

        # Plot 5: Brood by developmental stage (stacked area chart)
        ax5 = axes[2, 0]
        ax5.stackplot(days,
                     self.history['eggs'],
                     self.history['larvae'],
                     self.history['pupae'],
                     labels=['Eggs (Days 1-3)', 'Larvae (Days 4-8)', 'Pupae (Days 9-21)'],
                     colors=['#FFF3B0', '#FFD93D', '#C77D0A'],
                     alpha=0.7)
        ax5.set_xlabel('Days')
        ax5.set_ylabel('Number of Cells')
        ax5.set_title('Brood Cells by Developmental Stage')
        ax5.legend(loc='upper left')
        ax5.grid(True, alpha=0.3)

        # Plot 6: Brood cell occupancy percentage
        ax6 = axes[2, 1]
        ax6.plot(days, self.history['brood_occupancy_pct'], 'r-', linewidth=2)
        ax6.set_xlabel('Days')
        ax6.set_ylabel('Occupancy (%)')
        ax6.set_title('Brood Cell Occupancy')
        ax6.set_ylim(0, 100)
        ax6.axhline(y=80, color='orange', linestyle='--', linewidth=1, label='80% (High)')
        ax6.axhline(y=50, color='yellow', linestyle='--', linewidth=1, label='50% (Medium)')
        ax6.fill_between(days, self.history['brood_occupancy_pct'], alpha=0.3, color='red')
        ax6.legend(loc='upper left')
        ax6.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()


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
