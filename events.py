import random

def global_events(game_state, log_callback=None):
    """
    Triggers global events. If log_callback is provided, we log messages there.
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    events = [
        {"name": "Massive Data Leak", "visibility_increase": 5, "target": "random"},
        {"name": "International Scandal Exposes Espionage Network", "visibility_increase": 8, "target": "random"},
        {"name": "Cyber Attack on Global Financial Markets", "budget_loss": True, "target": "global"},
        {"name": "Whistleblower Exposes Covert Ops", "visibility_increase": 10, "target": "random"},
        {"name": "Successful Disinformation Campaign", "political_capital_gain": 5, "target": "random"}
    ]
    event = random.choice(events)
    log(f"Global Event: {event['name']}")

    if event['target'] == "global":
        affected_agencies = ["CIA", "Mossad", "MSS", "FSB"]
    elif event['target'] == "random":
        affected_agencies = random.sample(["CIA", "Mossad", "MSS", "FSB"], random.choice([1, 2]))

    for agency in affected_agencies:
        apply_event_effects(game_state, event, agency, log)

def apply_event_effects(game_state, event, agency, log):
    is_player = (agency == game_state['agency'])

    if 'visibility_increase' in event:
        if is_player:
            game_state['visibility'] += event['visibility_increase']
            log(f"{agency} (You) visibility +{event['visibility_increase']}, now {game_state['visibility']}%")
        else:
            game_state['visibility_tracker'][agency] += event['visibility_increase']
            log(f"{agency} visibility +{event['visibility_increase']}, now {game_state['visibility_tracker'][agency]}%")

    if 'budget_loss' in event and event['budget_loss']:
        budget_loss = random.randint(20, 50)
        if is_player:
            old_budget = game_state['budget']
            game_state['budget'] = max(0, old_budget - budget_loss)
            log(f"{agency} (You) lost ${budget_loss} from budget, now ${game_state['budget']}.")
        elif agency in game_state['ai_resources']:
            old_budget = game_state['ai_resources'][agency]['budget']
            game_state['ai_resources'][agency]['budget'] = max(0, old_budget - budget_loss)
            log(f"{agency} lost ${budget_loss} from their budget, now ${game_state['ai_resources'][agency]['budget']}.")

    if 'political_capital_gain' in event:
        if is_player:
            game_state['political_capital'] += event['political_capital_gain']
            log(f"{agency} (You) gained {event['political_capital_gain']} political capital, now {game_state['political_capital']}.")
        elif agency in game_state['ai_resources']:
            old_pc = game_state['ai_resources'][agency]['political_capital']
            game_state['ai_resources'][agency]['political_capital'] += event['political_capital_gain']
            log(f"{agency} gained {event['political_capital_gain']} political capital, now {game_state['ai_resources'][agency]['political_capital']}.")
