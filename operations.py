import random

# Define operations with costs and benefits
OPERATIONS = {
    "Politician Entrapment": {"budget": 100, "capital": 15, "success_chance": 0.2, "influence_gain": 30, "rival_influence_loss": 5, "populism_change": 10, "stability_change": -20, "visibility_increase": 10},
    "Covert Ops": {"budget": 75, "capital": 10, "success_chance": 0.6, "influence_gain": 5, "rival_influence_loss": 2, "populism_change": 0, "stability_change": 0, "visibility_increase": 1},
    "Cyber Warfare": {"budget": 40, "capital": 5, "success_chance": 0.55, "influence_gain": 5, "rival_influence_loss": 0, "populism_change": 0, "stability_change": 0, "visibility_increase": 3},
    "Crypto Scam": {"budget": 100, "capital": 1, "success_chance": 0.4, "influence_gain": 20, "rival_influence_loss": 0, "populism_change": -5, "stability_change": -5, "visibility_increase": 6},
    "Population Control": {"budget": 60, "capital": 8, "success_chance": 0.65, "influence_gain": 6, "rival_influence_loss": 0, "populism_change": 0, "stability_change": -5, "visibility_increase": 4},
    "Propaganda": {"budget": 25, "capital": 3, "success_chance": 0.5, "influence_gain": 4, "rival_influence_loss": 0, "populism_change": 0, "stability_change": 0, "visibility_increase": 4},
    "Frame Rivals": {"budget": 10, "capital": 15, "success_chance": 0.5, "influence_gain": 0, "rival_influence_loss": 40, "populism_change": 0, "stability_change": 0, "visibility_increase": 5}
}

def perform_operation(game_state):
    """Select and perform an operation directly (no mini-menu)."""
    operation = select_operation(game_state)
    if not operation:
        return

    target_country = select_target_country(game_state)
    if not target_country:
        return

    op_data = OPERATIONS[operation]

    if game_state['budget'] < op_data['budget'] or game_state['political_capital'] < op_data['capital']:
        print("Not enough budget or political capital for this operation.")
        return

    # Deduct costs
    game_state['budget'] -= op_data['budget']
    game_state['political_capital'] -= op_data['capital']

    print(f"\nPerforming {operation} in {target_country}...")

    # Operation success check
    success = random.random() < op_data['success_chance']

    if success:
        print(f"The {operation} in {target_country} was successful!")
        game_state['countries'][target_country]['influence'][game_state['agency']] += op_data['influence_gain']

        game_state['countries'][target_country]['populism_risk'] += op_data.get('populism_change', 0)
        game_state['countries'][target_country]['stability'] += op_data.get('stability_change', 0)

        reduce_rival_influence(game_state, target_country, op_data['rival_influence_loss'])
    else:
        print(f"The {operation} in {target_country} failed.")
        print(f"The failed operation drew extra attention.")

    # Apply visibility increase (doubled on failure)
    if success:
        visibility_increase = op_data.get('visibility_increase', 2)
    else:
        visibility_increase = op_data.get('visibility_increase', 2) * 2
        print(f"Visibility increased by {visibility_increase}% due to the failed operation.")

    game_state['visibility'] += visibility_increase
    print(f"Current Visibility: {game_state['visibility']}%")

def select_operation(game_state):
    """Prompts player to select an operation, showing costs and benefits."""
    print("\nAvailable Operations (Costs and Benefits):")

    for idx, (name, details) in enumerate(OPERATIONS.items(), 1):
        print(f"{idx}. {name} - Budget: {details['budget']}, Political Capital: {details['capital']}, Success Chance: {int(details['success_chance'] * 100)}%")

    choice = input("\nSelect operation: ").strip()

    operation_names = list(OPERATIONS.keys())

    if choice.isdigit():
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(operation_names):
            return operation_names[choice_index]

    print("Invalid choice. Operation skipped.")
    return None

def select_target_country(game_state):
    """Prompts player to choose a valid target country."""
    countries = list(game_state['countries'].keys())
    for idx, country in enumerate(countries, start=1):
        print(f"{idx}. {country}")

    choice = input("Select target country: ").strip()

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(countries):
            return countries[index]

    print("Invalid country selection. No operation performed.")
    return None

def reduce_rival_influence(game_state, country, amount):
    """Reduces rival agencies' influence in a target country."""
    for rival in ["CIA", "Mossad", "MSS", "FSB"]:
        if rival != game_state['agency']:
            game_state['countries'][country]['influence'][rival] = max(
                0, game_state['countries'][country]['influence'][rival] - amount
            )

def view_agency_visibility(game_state):
    """Shows visibility levels for all agencies."""
    print("\n--- Agency Visibility Levels ---")
    player = game_state['agency']
    for agency, visibility in game_state['visibility_tracker'].items():
        if agency == player:
            print(f"{agency} (You): {game_state['visibility']}%")
        else:
            print(f"{agency}: {visibility}%")

def view_global_influence(game_state):
    """Displays global influence for all countries and agencies, plus populism risk and stability."""
    print("\n--- Global Influence Report ---")
    # Add two new columns: Populism Risk (Pop Risk) and Stability (Stability)
    print(f"{'Country':<15} {'CIA':<8} {'Mossad':<8} {'MSS':<8} {'FSB':<8} {'Pop Risk':<9} {'Stability':<9}")

    for country, data in game_state['countries'].items():
        influences = data['influence']
        pop_risk = data['populism_risk']
        stability = data['stability']

        # Print each row including the new columns
        print(f"{country:<15} "
              f"{influences['CIA']:<8} "
              f"{influences['Mossad']:<8} "
              f"{influences['MSS']:<8} "
              f"{influences['FSB']:<8} "
              f"{pop_risk:<9} "
              f"{stability:<9}")
