"""
Simulation Plotter - Visualizations for bee colony simulations.

This module handles all plotting for bee simulation results,
supporting both base BeeHiveSimulator and SeasonalBeeSimulator.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class SimulationPlotter:
    """
    Handles all visualizations for bee colony simulations.

    Supports both BeeHiveSimulator and SeasonalBeeSimulator results.
    Automatically detects simulator type and provides appropriate plots.
    """

    def __init__(self, results: dict):
        """
        Initialize plotter with simulation results.

        Args:
            results: Dictionary returned by simulator.to_dataframes()
        """
        self.results = results
        self.metadata = results['metadata']
        self.population = results['population']
        self.dynamics = results['dynamics']

        # Seasonal-specific data
        self.is_seasonal = 'calendar' in results
        if self.is_seasonal:
            self.calendar = results['calendar']
            self.resources = results['resources']

    def plot_all(self):
        """Create comprehensive visualization."""
        if self.is_seasonal:
            self._plot_all_seasonal()
        else:
            self._plot_all_base()

    def _plot_all_base(self):
        """Create 6-plot figure for base simulator."""
        fig, axes = plt.subplots(3, 2, figsize=(14, 15))
        fig.suptitle('Bee Colony Population Dynamics', fontsize=16, fontweight='bold')

        days = self.population.index.values

        # Plot 1: Adult bee population
        ax1 = axes[0, 0]
        ax1.plot(days, self.population['adult_bees'], 'b-', linewidth=2)
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Adult Bees')
        ax1.set_title('Adult Bee Population')
        ax1.grid(True, alpha=0.3)
        ax1.fill_between(days, self.population['adult_bees'], alpha=0.3)

        # Plot 2: Brood population
        ax2 = axes[0, 1]
        ax2.plot(days, self.population['total_brood'], 'g-', linewidth=2)
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Developing Brood')
        ax2.set_title('Total Brood (Eggs, Larvae, Pupae)')
        ax2.grid(True, alpha=0.3)
        ax2.fill_between(days, self.population['total_brood'], alpha=0.3, color='green')

        # Plot 3: Daily egg laying and bee emergence
        ax3 = axes[1, 0]
        ax3.plot(days, self.dynamics['eggs_laid'], 'orange', linewidth=2, label='Eggs Laid')
        ax3.plot(days, self.dynamics['bees_emerged'], 'purple', linewidth=2, label='Bees Emerged')
        ax3.set_xlabel('Days')
        ax3.set_ylabel('Number of Bees')
        ax3.set_title('Daily Egg Laying vs Bee Emergence')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Net daily change
        ax4 = axes[1, 1]
        net_change = self.dynamics['net_change']
        colors = ['green' if x >= 0 else 'red' for x in net_change]
        ax4.bar(days, net_change, color=colors, alpha=0.6)
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Net Change in Adult Bees')
        ax4.set_title('Daily Population Change (Emerged - Died)')
        ax4.grid(True, alpha=0.3, axis='y')

        # Plot 5: Brood by developmental stage
        ax5 = axes[2, 0]
        ax5.stackplot(days,
                     self.population['eggs'],
                     self.population['larvae'],
                     self.population['pupae'],
                     labels=['Eggs (Days 1-3)', 'Larvae (Days 4-8)', 'Pupae (Days 9-21)'],
                     colors=['#FFF3B0', '#FFD93D', '#C77D0A'],
                     alpha=0.7)
        ax5.set_xlabel('Days')
        ax5.set_ylabel('Number of Cells')
        ax5.set_title('Brood Cells by Developmental Stage')
        ax5.legend(loc='upper left')
        ax5.grid(True, alpha=0.3)

        # Plot 6: Brood cell occupancy
        ax6 = axes[2, 1]
        ax6.plot(days, self.population['brood_occupancy_pct'], 'r-', linewidth=2)
        ax6.set_xlabel('Days')
        ax6.set_ylabel('Occupancy (%)')
        ax6.set_title('Brood Cell Occupancy')
        ax6.set_ylim(0, 100)
        ax6.axhline(y=80, color='orange', linestyle='--', linewidth=1, label='80% (High)')
        ax6.axhline(y=50, color='yellow', linestyle='--', linewidth=1, label='50% (Medium)')
        ax6.fill_between(days, self.population['brood_occupancy_pct'], alpha=0.3, color='red')
        ax6.legend(loc='upper left')
        ax6.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def _plot_all_seasonal(self):
        """Create 8-plot figure for seasonal simulator."""
        location_name = self.metadata.get('calendar_info', {}).get('location_name', 'Unknown')
        fig, axes = plt.subplots(4, 2, figsize=(16, 18))
        fig.suptitle(f'Seasonal Bee Colony Dynamics - {location_name}',
                     fontsize=16, fontweight='bold')

        days = self.population.index.values
        dates = self.calendar['calendar_date'].values

        # Determine x-axis tick positions
        tick_indices = list(range(0, len(days), 30))
        if len(days) - 1 not in tick_indices:
            tick_indices.append(len(days) - 1)

        # Plot 1: Adult bee population
        ax1 = axes[0, 0]
        ax1.plot(days, self.population['adult_bees'], 'b-', linewidth=2)
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Adult Bees')
        ax1.set_title('Adult Bee Population')
        ax1.set_xticks([days[i] for i in tick_indices])
        ax1.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        ax1.fill_between(days, self.population['adult_bees'], alpha=0.3)

        # Plot 2: Total brood
        ax2 = axes[0, 1]
        ax2.plot(days, self.population['total_brood'], 'g-', linewidth=2)
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Developing Brood')
        ax2.set_title('Total Brood (Eggs, Larvae, Pupae)')
        ax2.set_xticks([days[i] for i in tick_indices])
        ax2.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
        ax2.fill_between(days, self.population['total_brood'], alpha=0.3, color='green')

        # Plot 3: Calendar-modulated rates
        ax3 = axes[1, 0]
        ax3.plot(days, self.calendar['effective_egg_rate'], 'orange', linewidth=2, label='Egg Laying Rate')
        ax3.plot(days, self.calendar['effective_attrition'], 'brown', linewidth=2, label='Attrition Rate')
        ax3.set_xlabel('Days')
        ax3.set_ylabel('Bees per Day')
        ax3.set_title('Calendar-Modulated Rates')
        ax3.set_xticks([days[i] for i in tick_indices])
        ax3.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Daily population change
        ax4 = axes[1, 1]
        net_change = self.dynamics['net_change']
        colors = ['green' if x >= 0 else 'red' for x in net_change]
        ax4.bar(days, net_change, color=colors, alpha=0.6)
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Net Change in Adult Bees')
        ax4.set_title('Daily Population Change (Emerged - Died)')
        ax4.set_xticks([days[i] for i in tick_indices])
        ax4.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')
        ax4.grid(True, alpha=0.3, axis='y')

        # Plot 5: Seasonal forage availability
        ax5 = axes[2, 0]
        ax5.plot(days, self.calendar['nectar_availability'], 'gold', linewidth=2, label='Nectar')
        ax5.plot(days, self.calendar['pollen_availability'], 'brown', linewidth=2, label='Pollen')
        ax5.set_xlabel('Days')
        ax5.set_ylabel('Availability (0-1)')
        ax5.set_title('Seasonal Forage Availability')
        ax5.set_xticks([days[i] for i in tick_indices])
        ax5.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_ylim(0, 1)

        # Plot 6: Honey stores with supering markers
        ax6 = axes[2, 1]
        ax6.plot(days, self.resources['honey_stores'], 'gold', linewidth=2, label='Honey Stores')
        ax6.fill_between(days, 0, 8, color='yellow', alpha=0.2, label='Min for supering (8kg)')
        ax6.fill_between(days, 8, 15, color='yellow', alpha=0.1, label='Good reserves (15kg)')
        # Mark supering recommendations
        super_days = [idx for idx in self.resources.index if self.resources.loc[idx, 'supering_recommendation']]
        if super_days:
            super_stores = [self.resources.loc[idx, 'honey_stores'] for idx in super_days]
            ax6.scatter(super_days, super_stores, color='red', s=100, marker='^',
                       label='ADD SUPER HERE', zorder=5)
        ax6.set_xlabel('Days')
        ax6.set_ylabel('Honey (kg)')
        ax6.set_title('Honey Stores & Supering Recommendations')
        ax6.set_xticks([days[i] for i in tick_indices])
        ax6.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')
        ax6.legend(loc='upper left', fontsize=8)
        ax6.grid(True, alpha=0.3)

        # Plot 7: Daily honey production vs consumption
        ax7 = axes[3, 0]
        ax7.fill_between(days, self.resources['daily_honey_production'],
                        color='green', alpha=0.5, label='Production')
        ax7.fill_between(days, -self.resources['daily_honey_consumption'],
                        color='red', alpha=0.5, label='Consumption')
        ax7.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax7.set_xlabel('Days')
        ax7.set_ylabel('Honey (kg/day)')
        ax7.set_title('Daily Honey Production vs Consumption')
        ax7.set_xticks([days[i] for i in tick_indices])
        ax7.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')
        ax7.legend()
        ax7.grid(True, alpha=0.3)

        # Plot 8: Brood occupancy with 70% threshold
        ax8 = axes[3, 1]
        ax8.plot(days, self.population['brood_occupancy_pct'], 'r-', linewidth=2, label='Occupancy')
        ax8.axhline(y=80, color='orange', linestyle='--', linewidth=1, label='80% (High)')
        ax8.axhline(y=70, color='red', linestyle='--', linewidth=1.5, label='70% (Super threshold)')
        ax8.axhline(y=50, color='yellow', linestyle='--', linewidth=1, label='50% (Medium)')
        ax8.fill_between(days, self.population['brood_occupancy_pct'], alpha=0.3, color='red')
        ax8.set_xlabel('Days')
        ax8.set_ylabel('Occupancy (%)')
        ax8.set_title('Brood Cell Occupancy (hover over points for details)')
        ax8.set_xticks([days[i] for i in tick_indices])
        ax8.set_xticklabels([dates[i] for i in tick_indices], rotation=45, ha='right')
        ax8.set_ylim(0, 100)
        ax8.legend(loc='upper left', fontsize=8)
        ax8.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()
