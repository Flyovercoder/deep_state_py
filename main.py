import json
from operations import perform_operation, view_agency_visibility, view_global_influence
from ai import rival_turn
from events import global_events

def load_countries():
    try:
        with open('data/countries.json', 'r') as file:
            # print("Countries data loaded successfully.")
            return json.load(file)
    except Exception as e:
        print(f"Error loading countries data: {e}")
        exit()

def save_game(state):
    try:
        with open('save/save1.json', 'w') as file:
            json.dump(state, file, indent=4)
        # print("Game saved.")
    except Exception as e:
        print(f"Error saving game: {e}")

def get_starting_resources(agency):
    starting_resources = {
        'CIA': {'budget': 200, 'political_capital': 50},
        'Mossad': {'budget': 150, 'political_capital': 40},
        'MSS': {'budget': 250, 'political_capital': 60},
        'FSB': {'budget': 180, 'political_capital': 45}
    }
    return starting_resources.get(agency, {'budget': 100, 'political_capital': 10})

def initialize_ai_resources(player_agency):
    rivals = ['CIA', 'Mossad', 'MSS', 'FSB']
    rivals.remove(player_agency)

    ai_resources = {}
    for rival in rivals:
        resources = get_starting_resources(rival)
        ai_resources[rival] = {
            "budget": resources['budget'],
            "political_capital": resources['political_capital'],
            "research_points": 0,
            "agents": 1,
            "researched_techs": []
        }

    return ai_resources

def award_country_rewards(game_state):
    """
    Gives budget/capital rewards to the agency leading in each country,
    as long as that country is stable and not too populist.
    """
    for country, data in game_state['countries'].items():
        if data['populism_risk'] > 50 or data['stability'] < 50:
            continue

        leading_agency = max(data['influence'], key=data['influence'].get)

        if leading_agency == game_state['agency']:
            game_state['budget'] += data.get('budget_reward', 0)
            game_state['political_capital'] += data.get('capital_reward', 0)
        else:
            if leading_agency not in game_state['ai_resources']:
                game_state['ai_resources'][leading_agency] = {'budget': 0, 'political_capital': 0}

            game_state['ai_resources'][leading_agency]['budget'] += data.get('budget_reward', 0)
            game_state['ai_resources'][leading_agency]['political_capital'] += data.get('capital_reward', 0)

def display_resource_summary(game_state):
    """
    Returns a string summarizing resources for the player and the AI, instead of printing.
    """
    lines = []
    lines.append("\n--- Resource Summary ---")
    lines.append(f"{game_state['agency']} (You) - Budget: ${game_state['budget']}, "
                 f"Political Capital: {game_state['political_capital']}, Agents: {game_state['agents']}, "
                 f"Research Points: {game_state['research_points']}")

    for agency, resources in game_state['ai_resources'].items():
        lines.append(f"{agency} - Budget: ${resources['budget']}, "
                     f"Political Capital: {resources['political_capital']}")
    return "\n".join(lines)

def research_technology(game_state):
    """
    This function used to prompt for user input (tech choice).
    Now it only returns a list of available techs or attempts to research a given tech name.
    You can integrate it with your Tkinter UI to pick which tech to research.
    """
    with open('data/tech_tree.json', 'r') as file:
        tech_tree = json.load(file)

    available_techs = {name: data for name, data in tech_tree.items() if name not in game_state['researched_techs']}
    return available_techs  # The UI can display these and let the user pick.

def apply_tech_choice(game_state, tech_name, tech_data):
    """
    Actually applies the chosen tech, deducting cost & reducing visibility.
    """
    if game_state['research_points'] < tech_data['cost']:
        return False, "Not enough research points to unlock this technology."

    game_state['research_points'] -= tech_data['cost']
    reduction = tech_data['visibility_reduction']
    game_state['visibility'] = max(0, game_state['visibility'] - reduction)
    game_state['researched_techs'].append(tech_name)

    return True, f"{tech_name} researched! Visibility reduced by {reduction}%"

def buy_agent(game_state):
    """
    Attempts to buy a new agent (cost: 200 budget + 50 capital).
    Returns success/failure message.
    """
    if game_state['budget'] >= 200 and game_state['political_capital'] >= 50:
        game_state['budget'] -= 200
        game_state['political_capital'] -= 50
        game_state['agents'] += 1
        return True, "You have recruited a new agent!"
    else:
        return False, "Not enough budget or political capital to recruit an agent."

def check_win_conditions(game_state):
    """Checks all player win conditions."""
    if check_global_domination(game_state):
        return True, "Your agency has established global dominance. You Win!"

    if check_shadow_victory(game_state):
        return True, "You are the last unexposed agency. You Win!"

    return False, ""

def check_global_domination(game_state):
    """Win if player has 80%+ influence in 60% of countries."""
    controlled_countries = 0
    total_countries = len(game_state['countries'])

    for country, data in game_state['countries'].items():
        if game_state['agency'] in data['influence'] and data['influence'][game_state['agency']] >= 80:
            controlled_countries += 1

    return (controlled_countries / total_countries) >= 0.6

def check_shadow_victory(game_state):
    """Win if all rival agencies have at least 98% visibility."""
    for rival, visibility in game_state['visibility_tracker'].items():
        if rival != game_state['agency'] and visibility < 98:
            return False
    return True

def select_agency_cli():
    """Old console-based agency selection for fallback or debug."""
    print("Select your Agency:")
    print("1. CIA (USA)")
    print("2. Mossad (Israel)")
    print("3. MSS (China)")
    print("4. FSB (Russia)")

    choice = input("> ").strip()
    return ["CIA", "Mossad", "MSS", "FSB"][int(choice) - 1] if choice in ["1", "2", "3", "4"] else "CIA"

def initialize_game(agency=None):
    """
    If agency is None, defaults to CIA.
    Otherwise use the given agency string (CIA, Mossad, MSS, FSB).
    Returns a fresh game_state dictionary.
    """
    if not agency:
        agency = "CIA"

    countries = load_countries()
    resources = get_starting_resources(agency)

    game_state = {
        'turn': 1,
        'agency': agency,
        'countries': countries,
        'budget': resources['budget'],
        'political_capital': resources['political_capital'],
        'research_points': 0,
        'visibility': 5,
        'agents': 1,
        'agents_used': 0,
        'visibility_tracker': {
            'CIA': 20,
            'Mossad': 10,
            'MSS': 5,
            'FSB': 10
        },
        'ai_resources': initialize_ai_resources(agency),
        'researched_techs': []
    }
    return game_state

# We remove the console-based main loop here to let tkinter (or any other UI) drive the flow.
