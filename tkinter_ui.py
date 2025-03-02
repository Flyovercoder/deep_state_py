import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import tkinter.font as tkFont

import main
import operations
import ai
import events

class DeepStateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deep State")

        self.selected_agency = None
        self.game_state = None

        # 1) Agency selection
        self.agency_frame = tk.Frame(self.root)
        self.agency_frame.pack(pady=10)

        tk.Label(self.agency_frame, text="Select Your Agency:").pack()
        self.agency_var = tk.StringVar(value="CIA")
        for ag in ["CIA", "Mossad", "MSS", "FSB"]:
            rb = tk.Radiobutton(self.agency_frame, text=ag, variable=self.agency_var, value=ag)
            rb.pack(anchor="w")

        confirm_btn = tk.Button(self.agency_frame, text="Confirm", command=self.start_game)
        confirm_btn.pack(pady=10)

        # 2) Main UI (hidden until confirm)
        self.main_frame = tk.Frame(self.root)
        self.create_main_ui()

    def start_game(self):
        """Called when user clicks 'Confirm' on agency selection."""
        self.selected_agency = self.agency_var.get()
        self.agency_frame.destroy()

        # Build initial game state
        countries_data = main.load_countries()
        resources = main.get_starting_resources(self.selected_agency)
        self.game_state = {
            'turn': 1,
            'agency': self.selected_agency,
            'countries': countries_data,
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
            'ai_resources': main.initialize_ai_resources(self.selected_agency),
            'researched_techs': []
        }

        self.main_frame.pack(padx=10, pady=10)
        self.update_labels()
        self.log(f"Game started as {self.selected_agency}.")

    def create_main_ui(self):
        """
        Sets up all widgets in the main UI, but doesn't show them
        until 'start_game()' is called and we do self.main_frame.pack().
        """

        # Resource labels
        label_frame = tk.Frame(self.main_frame)
        label_frame.pack(pady=5)

        self.budget_label = tk.Label(label_frame, text="Budget: 0")
        self.budget_label.grid(row=0, column=0, sticky="w")

        self.capital_label = tk.Label(label_frame, text="Political Capital: 0")
        self.capital_label.grid(row=1, column=0, sticky="w")

        self.research_label = tk.Label(label_frame, text="Research Points: 0")
        self.research_label.grid(row=2, column=0, sticky="w")

        self.visibility_label = tk.Label(label_frame, text="Visibility: 0%")
        self.visibility_label.grid(row=3, column=0, sticky="w")

        self.turn_label = tk.Label(label_frame, text="Turn: 1")
        self.turn_label.grid(row=4, column=0, sticky="w")

        # Agents
        self.total_agents_label = tk.Label(label_frame, text="Total Agents: 0")
        self.total_agents_label.grid(row=5, column=0, sticky="w")

        self.available_agents_label = tk.Label(label_frame, text="Available Agents: 0")
        self.available_agents_label.grid(row=6, column=0, sticky="w")

        # Buttons
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Perform Operation", command=self.perform_operation_dialog).grid(row=0, column=0, padx=5, pady=2)
        tk.Button(button_frame, text="Research Tech", command=self.research_tech_dialog).grid(row=0, column=1, padx=5, pady=2)
        tk.Button(button_frame, text="Buy Agent", command=self.buy_agent).grid(row=1, column=0, padx=5, pady=2)
        tk.Button(button_frame, text="View Visibility", command=self.view_visibility).grid(row=1, column=1, padx=5, pady=2)
        tk.Button(button_frame, text="View Influence", command=self.view_influence).grid(row=2, column=0, padx=5, pady=2)
        tk.Button(button_frame, text="End Turn", command=self.end_turn).grid(row=2, column=1, padx=5, pady=2)
        tk.Button(button_frame, text="Victory Conditions", command=self.show_victory_conditions).grid(row=3, column=0, columnspan=2, pady=2)

        # Log text area
        self.log_text = tk.Text(self.main_frame, width=110, height=10, wrap="none")
        self.log_text.pack(pady=5)

    def update_labels(self):
        """Refresh resource/turn/agent labels from game_state."""
        if not self.game_state:
            return
        gs = self.game_state
        self.budget_label.config(text=f"Budget: {gs['budget']}")
        self.capital_label.config(text=f"Political Capital: {gs['political_capital']}")
        self.research_label.config(text=f"Research Points: {gs['research_points']}")
        self.visibility_label.config(text=f"Visibility: {gs['visibility']}%")
        self.turn_label.config(text=f"Turn: {gs['turn']}")

        total_agents = gs['agents']
        available_agents = total_agents - gs['agents_used']
        self.total_agents_label.config(text=f"Total Agents: {total_agents}")
        self.available_agents_label.config(text=f"Available Agents: {available_agents}")

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    # --------------------------------------------------
    # Show Victory Conditions
    # --------------------------------------------------
    def show_victory_conditions(self):
        msg = (
            "Victory Conditions:\n\n"
            "1) Global Domination:\n"
            "   - Have 80%+ influence in at least 60% of countries.\n\n"
            "2) Shadow Victory:\n"
            "   - All rival agencies must have at least 98% visibility.\n\n"
            "Lose Condition:\n"
            "   - If your agency's visibility reaches 100%, you are exposed."
        )
        messagebox.showinfo("Victory Conditions", msg)

    # --------------------------------------------------
    # PERFORM OPERATION
    # --------------------------------------------------
    def perform_operation_dialog(self):
        if not self.game_state:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Perform Operation")

        tk.Label(dialog, text="Select Operation:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        op_options = list(operations.OPERATIONS.keys())
        op_var = tk.StringVar(dialog)
        op_box = ttk.Combobox(dialog, textvariable=op_var, values=op_options, state="readonly", width=30)
        op_box.grid(row=0, column=1, padx=5, pady=5)
        op_box.current(0)

        op_detail_label = tk.Label(dialog, text="", fg="blue")
        op_detail_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        def on_op_select(event):
            op_name = op_var.get()
            op_data = operations.OPERATIONS[op_name]
            cost_str = (f"Budget Cost: {op_data['budget']}, "
                        f"Cap Cost: {op_data['capital']}, "
                        f"Success: {int(op_data['success_chance']*100)}%")
            op_detail_label.config(text=cost_str)

        op_box.bind("<<ComboboxSelected>>", on_op_select)
        on_op_select(None)

        tk.Label(dialog, text="Select Country:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        country_options = list(self.game_state['countries'].keys())
        country_var = tk.StringVar(dialog)
        country_box = ttk.Combobox(dialog, textvariable=country_var, values=country_options, state="readonly", width=30)
        country_box.grid(row=2, column=1, padx=5, pady=5)
        country_box.current(0)

        def on_confirm():
            operation_name = op_var.get()
            country_name = country_var.get()
            dialog.destroy()
            self.perform_operation(operation_name, country_name)

        tk.Button(dialog, text="Confirm", command=on_confirm).grid(row=3, column=0, columnspan=2, pady=10)

    def perform_operation(self, op_name, country_name):
        gs = self.game_state
        if gs['agents_used'] >= gs['agents']:
            self.log("All agents used this turn.")
            return

        op_data = operations.OPERATIONS[op_name]
        if gs['budget'] < op_data['budget'] or gs['political_capital'] < op_data['capital']:
            self.log("Not enough budget or political capital.")
            return

        gs['budget'] -= op_data['budget']
        gs['political_capital'] -= op_data['capital']

        msg = f"Performing {op_name} in {country_name}... "
        success = (random.random() < op_data['success_chance'])

        if success:
            msg += "Success! "
            gs['countries'][country_name]['influence'][gs['agency']] += op_data['influence_gain']
            gs['countries'][country_name]['populism_risk'] += op_data.get('populism_change', 0)
            gs['countries'][country_name]['stability'] += op_data.get('stability_change', 0)
            self._reduce_rival_influence(country_name, op_data['rival_influence_loss'])
            vis_increase = op_data.get('visibility_increase', 2)
        else:
            msg += "Failed! Extra attention drawn. "
            vis_increase = op_data.get('visibility_increase', 2) * 2

        gs['visibility'] += vis_increase
        gs['agents_used'] += 1
        msg += f"Visibility +{vis_increase}, now {gs['visibility']}%."

        self.log(msg)
        self.update_labels()

    def _reduce_rival_influence(self, country_name, amt):
        for rival in ["CIA", "Mossad", "MSS", "FSB"]:
            if rival != self.game_state['agency']:
                current = self.game_state['countries'][country_name]['influence'][rival]
                self.game_state['countries'][country_name]['influence'][rival] = max(0, current - amt)

    # --------------------------------------------------
    # RESEARCH TECH
    # --------------------------------------------------
    def research_tech_dialog(self):
        if not self.game_state:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Research Tech")
        dialog.geometry("400x200")

        with open('data/tech_tree.json','r') as f:
            tech_tree = json.load(f)

        available_techs = {name: data for name, data in tech_tree.items()
                           if name not in self.game_state['researched_techs']}

        if not available_techs:
            messagebox.showinfo("Research", "All technologies have been researched.")
            dialog.destroy()
            return

        tk.Label(dialog, text="Select Tech:").grid(row=0, column=0, padx=5, pady=5, sticky="e")

        tech_var = tk.StringVar(dialog)
        tech_list = list(available_techs.keys())
        tech_box = ttk.Combobox(dialog, textvariable=tech_var, values=tech_list, state="readonly", width=35)
        tech_box.grid(row=0, column=1, padx=5, pady=5)
        tech_box.current(0)

        tech_detail_label = tk.Label(dialog, text="", fg="blue")
        tech_detail_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        def on_tech_select(event):
            t_name = tech_var.get()
            data = available_techs[t_name]
            cost = data['cost']
            reduction = data['visibility_reduction']
            detail_str = f"Cost: {cost}, Visibility Reduction: {reduction}"
            tech_detail_label.config(text=detail_str)

        tech_box.bind("<<ComboboxSelected>>", on_tech_select)
        on_tech_select(None)

        def on_confirm():
            chosen_tech = tech_var.get()
            cost = available_techs[chosen_tech]['cost']
            reduction = available_techs[chosen_tech]['visibility_reduction']

            if self.game_state['research_points'] < cost:
                self.log("Not enough research points.")
            else:
                old_vis = self.game_state['visibility']
                new_vis = max(0, old_vis - reduction)
                self.game_state['visibility'] = new_vis
                self.game_state['research_points'] -= cost
                self.game_state['researched_techs'].append(chosen_tech)
                msg = f"{chosen_tech} researched! Visibility -{reduction}, from {old_vis}% to {new_vis}%."
                self.log(msg)

            self.update_labels()
            dialog.destroy()

        tk.Button(dialog, text="Confirm", command=on_confirm).grid(row=2, column=0, columnspan=2, pady=10)

    # --------------------------------------------------
    # BUY AGENT
    # --------------------------------------------------
    def buy_agent(self):
        if not self.game_state:
            return
        can_buy, msg = main.buy_agent(self.game_state)
        self.log(msg)
        self.update_labels()

    # --------------------------------------------------
    # VIEW VISIBILITY
    # --------------------------------------------------
    def view_visibility(self):
        if not self.game_state:
            return
        gs = self.game_state
        lines = ["--- Agency Visibility Levels ---"]
        player = gs['agency']
        for ag, vis in gs['visibility_tracker'].items():
            if ag == player:
                lines.append(f"{ag} (You): {gs['visibility']}%")
            else:
                lines.append(f"{ag}: {vis}%")
        messagebox.showinfo("Visibility", "\n".join(lines))

    # --------------------------------------------------
    # VIEW INFLUENCE - Use a Toplevel with monospaced font
    # --------------------------------------------------
    def view_influence(self):
        if not self.game_state:
            return

        # We'll create a new Toplevel with a Text widget, using monospaced font
        inf_win = tk.Toplevel(self.root)
        inf_win.title("Global Influence")

        text_area = tk.Text(inf_win, width=80, height=10)
        text_area.pack(padx=10, pady=10)

        # Configure a monospaced font (Courier)
        font_mono = tkFont.Font(family="Courier", size=10)
        text_area.configure(font=font_mono)

        # Build our lines with careful spacing
        lines = []
        lines.append("--- Global Influence Report ---\n")

        # Let's do right-aligned for numeric columns
        # We'll do: Country(12, left) CIA(4, right) Mossad(5, right) MSS(4) FSB(4) PopRisk(6) Stability(6)
        # We'll try to keep them within 80 columns total
        header = f"{'Country':<12}{'CIA':>4}{'Mossad':>6}{'MSS':>5}{'FSB':>5}{'PopR':>6}{'Stab':>6}"
        lines.append(header)

        gs = self.game_state
        for country, data in gs['countries'].items():
            inf = data['influence']
            pop_risk = data['populism_risk']
            stab = data['stability']
            # Right align for numbers with :>4, etc.
            line = (f"{country:<12}"
                    f"{inf['CIA']:>4}"
                    f"{inf['Mossad']:>6}"
                    f"{inf['MSS']:>5}"
                    f"{inf['FSB']:>5}"
                    f"{pop_risk:>6}"
                    f"{stab:>6}")
            lines.append(line)

        # Insert lines into the text widget
        for ln in lines:
            text_area.insert(tk.END, ln + "\n")

        text_area.config(state=tk.DISABLED)  # make read-only

    # --------------------------------------------------
    # END TURN
    # --------------------------------------------------
    def end_turn(self):
        if not self.game_state:
            return

        # Rival turn w/ log callback
        ai.rival_turn(self.game_state, log_callback=self.log)

        # Global events w/ log callback
        events.global_events(self.game_state, log_callback=self.log)

        # Award country rewards
        main.award_country_rewards(self.game_state)

        # Check win conditions
        won, msg = main.check_win_conditions(self.game_state)
        if won:
            messagebox.showinfo("Victory!", msg)
            self.root.destroy()
            return

        # Increase resources
        self.game_state['turn'] += 1
        self.game_state['budget'] += 50
        self.game_state['political_capital'] += 5
        self.game_state['research_points'] += 3
        self.game_state['visibility'] += 1

        # Check for exposure
        if self.game_state['visibility'] >= 100:
            messagebox.showinfo("Game Over", "Your agency has been exposed!")
            self.root.destroy()
            return

        # Reset agents
        self.game_state['agents_used'] = 0

        # Save & update
        main.save_game(self.game_state)
        self.update_labels()
        self.log(f"End of Turn {self.game_state['turn'] - 1}. Starting Turn {self.game_state['turn']}.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeepStateApp(root)
    root.mainloop()
