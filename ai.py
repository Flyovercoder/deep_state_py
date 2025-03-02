import random
import json

AI_OPERATIONS = {
    "Political Influence": {"budget": 20, "capital": 3, "success_chance": 0.6, "influence_gain": 5, "visibility_increase": 2},
    "Covert Ops": {"budget": 50, "capital": 7, "success_chance": 0.55, "influence_gain": 7, "visibility_increase": 3},
    "Cyber Warfare": {"budget": 40, "capital": 5, "success_chance": 0.5, "influence_gain": 5, "visibility_increase": 3},
    "Economic Pressure": {"budget": 30, "capital": 4, "success_chance": 0.5, "influence_gain": 4, "visibility_increase": 2},
    "Propaganda": {"budget": 25, "capital": 3, "success_chance": 0.6, "influence_gain": 3, "visibility_increase": 1}
}

def load_tech_tree():
    with open('data/tech_tree.json', 'r') as file:
        return json.load(file)

TECH_TREE = load_tech_tree()

def rival_turn(game_state, log_callback=None):
    """
    Process each rival agency's turn.
    If log_callback is provided, it should be a function that accepts a string, e.g., log_callback("some message").
    Otherwise, we default to print statements.
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    rivals = ["CIA", "Mossad", "MSS", "FSB"]
    rivals.remove(game_state['agency'])

    for rival in rivals:
        ai_data = game_state['ai_resources'].get(rival, {
            "budget": 0, "political_capital": 0, "research_points": 0, "agents": 1, "researched_techs": []
        })

        # Passive visibility increase
        game_state['visibility_tracker'][rival] += 1

        # Add passive research points
        ai_data['research_points'] += 3

        if game_state['visibility_tracker'][rival] >= 100:
            log(f"{rival} is frozen due to exposure and can only research or buy agents.")
            ai_research_tech(game_state, rival, ai_data, log)
            ai_buy_agent(game_state, rival, ai_data, log)
            game_state['ai_resources'][rival] = ai_data
            continue

        # Try to buy agents before operations
        ai_buy_agent(game_state, rival, ai_data, log)

        target_country = pick_target_country(game_state, rival)
        operation = pick_affordable_operation(ai_data)

        if operation is None:
            log(f"{rival} skips a turn due to lack of resources.")
            ai_research_tech(game_state, rival, ai_data, log)
            game_state['ai_resources'][rival] = ai_data
            continue

        log(f"{rival} is conducting {operation} in {target_country}...")

        op_data = AI_OPERATIONS[operation]
        if ai_data['budget'] < op_data['budget'] or ai_data['political_capital'] < op_data['capital']:
            log(f"{rival} cannot afford {operation} this turn.")
            ai_research_tech(game_state, rival, ai_data, log)
            game_state['ai_resources'][rival] = ai_data
            continue

        # Pay for operation
        ai_data['budget'] -= op_data['budget']
        ai_data['political_capital'] -= op_data['capital']

        success = random.random() < op_data['success_chance']
        if success:
            log(f"{rival} successfully increases influence in {target_country}.")
            game_state['countries'][target_country]['influence'][rival] += op_data['influence_gain']
            visibility_increase = op_data.get('visibility_increase', 2)
        else:
            log(f"{rival}'s {operation} failed in {target_country}.")
            visibility_increase = op_data.get('visibility_increase', 2) * 2

        game_state['visibility_tracker'][rival] += visibility_increase

        ai_research_tech(game_state, rival, ai_data, log)
        game_state['ai_resources'][rival] = ai_data

def ai_research_tech(game_state, rival, ai_data, log):
    if rival in ai_data['researched_techs']:
        return
    available_techs = {name: data for name, data in TECH_TREE.items() if name not in ai_data['researched_techs']}

    if not available_techs:
        return

    # Prioritize visibility reduction if high
    if game_state['visibility_tracker'][rival] >= 60:
        sorted_techs = sorted(available_techs.items(), key=lambda x: -x[1]['visibility_reduction'])
    else:
        sorted_techs = list(available_techs.items())

    for tech_name, tech_data in sorted_techs:
        if ai_data['research_points'] >= tech_data['cost']:
            ai_data['research_points'] -= tech_data['cost']
            ai_data['researched_techs'].append(tech_name)
            old_vis = game_state['visibility_tracker'][rival]
            game_state['visibility_tracker'][rival] = max(0, old_vis - tech_data['visibility_reduction'])
            log(f"{rival} researched {tech_name}, reducing visibility from {old_vis} to {game_state['visibility_tracker'][rival]}.")
            break

def ai_buy_agent(game_state, rival, ai_data, log):
    if ai_data['budget'] >= 200 and ai_data['political_capital'] >= 50:
        ai_data['budget'] -= 200
        ai_data['political_capital'] -= 50
        ai_data['agents'] += 1
        log(f"{rival} recruited a new agent.")

def pick_target_country(game_state, rival):
    countries = list(game_state['countries'].keys())
    weighted_countries = []
    for country in countries:
        influence = game_state['countries'][country]['influence']
        rival_influence = influence.get(rival, 0)
        player_influence = influence.get(game_state['agency'], 0)

        weight = 1
        if rival_influence > 20:
            weight += 3
        if player_influence > 15:
            weight += 2

        weighted_countries.extend([country] * weight)

    return random.choice(weighted_countries)

def pick_affordable_operation(ai_resources):
    affordable_ops = [
        op for op, data in AI_OPERATIONS.items()
        if ai_resources['budget'] >= data['budget'] and ai_resources['political_capital'] >= data['capital']
    ]
    if not affordable_ops:
        return None
    affordable_ops.sort(key=lambda op: AI_OPERATIONS[op]['budget'], reverse=True)
    return affordable_ops[0]
