from __future__ import annotations

from pathlib import Path

from app.file_io import load_customer_groups, load_restaurant_settings, save_simulation_result
from app.models import CustomerGroup, QueueRule, SimulationResult, Table
from app.simulator import format_result, run_simulation


def _prompt_path(prompt: str) -> str:
    return input(prompt).strip().strip('"')


def main() -> None:
    restaurant_name = ""
    scenario_name = ""
    service_threshold = 15
    turnover_duration = 0
    queue_rules: list[QueueRule] = []
    tables: list[Table] = []
    groups: list[CustomerGroup] = []
    result: SimulationResult | None = None

    while True:
        print("\nRestaurant Queue Simulation")
        print("1. Load restaurant settings")
        print("2. Load customer arrivals")
        print("3. Run simulation")
        print("4. View results")
        print("5. Save results")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()
        try:
            if choice == "1":
                path = _prompt_path("Path to restaurant settings JSON: ")
                restaurant_name, service_threshold, turnover_duration, queue_rules, tables = load_restaurant_settings(path)
                result = None
                print(f"Loaded restaurant settings for '{restaurant_name}'.")
            elif choice == "2":
                path = _prompt_path("Path to customer arrivals JSON: ")
                scenario_name, groups = load_customer_groups(path)
                result = None
                print(f"Loaded scenario '{scenario_name}' with {len(groups)} groups.")
            elif choice == "3":
                if not queue_rules or not tables:
                    print("Please load restaurant settings first.")
                    continue
                if not scenario_name:
                    print("Please load customer arrivals first.")
                    continue
                result = run_simulation(
                    restaurant_name=restaurant_name,
                    scenario_name=scenario_name,
                    queue_rules=queue_rules,
                    tables=tables,
                    groups=groups,
                    service_threshold=service_threshold,
                    turnover_duration=turnover_duration,
                )
                print("Simulation completed.")
            elif choice == "4":
                if result is None:
                    print("No result available. Run the simulation first.")
                    continue
                print()
                print(format_result(result))
            elif choice == "5":
                if result is None:
                    print("No result available. Run the simulation first.")
                    continue
                path = _prompt_path("Path to save results JSON: ")
                saved_path = save_simulation_result(path, result)
                print(f"Results saved to {saved_path}.")
            elif choice == "6":
                print("Exiting program.")
                return
            else:
                print("Invalid option. Please choose a number from 1 to 6.")
        except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
