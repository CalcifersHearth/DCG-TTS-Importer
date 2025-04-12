import tkinter as tk
from tkinter import messagebox, filedialog
import re
import json
import os

# ----------- Deck Parsing Function -----------
def parse_decklist(deck_text):
    main_deck = []
    egg_deck = []
    current_section = "main"

    # Split the deck list into lines
    for line in deck_text.strip().splitlines():
        line = line.strip()

        # Skip comments and empty lines; switch to egg deck if line indicates so
        if not line or line.startswith("//"):
            if line.lower().startswith("// egg"):
                current_section = "egg"
            continue

        # Match: Quantity Card Name Set-Number
        match = re.match(r"(\d+)\s+(.+)\s+([A-Z0-9\-]+)", line)
        if match:
            count, name, code = match.groups()
            card = {"count": int(count), "name": name.strip(), "code": code.strip()}
            if current_section == "main":
                main_deck.append(card)
            else:
                egg_deck.append(card)
        else:
            print(f"[WARN] Line not recognized: {line}")

    return main_deck, egg_deck

# ----------- Card Image URL Lookup -----------
def get_card_image_url(code):
    return f"https://images.digimoncard.io/images/cards/{code}.jpg"

# ----------- Build the Deck for TTS (JSON for Custom Deck Import) -----------
def build_tts_deck(deck_name, main_deck, egg_deck):
    # Process Main Deck:
    main_custom_deck = {}
    main_cards = []
    main_ids = []
    card_id = 100

    for card in main_deck:
        count = card["count"]
        name = card["name"]
        code = card["code"]
        image_url = get_card_image_url(code)

        # Determine the custom deck group key from card_id (e.g., 100 => "1")
        deck_index = str(card_id // 100)
        if deck_index not in main_custom_deck:
            main_custom_deck[deck_index] = {
                "FaceURL": image_url,
                "BackURL": "https://images.digimoncard.io/images/assets/CardBack.jpg",  # Main deck back image
                "NumWidth": 1,
                "NumHeight": 1,
                "BackIsHidden": True
            }

        # For each copy of the card, add a full card object with Transform and Nickname
        for _ in range(count):
            main_cards.append({
                "Name": "Card",
                "Nickname": name,
                "CardID": card_id,
                "Transform": {
                    "posX": 0,
                    "posY": 3,
                    "posZ": 0,
                    "rotX": 0,
                    "rotY": 180,
                    "rotZ": 180,
                    "scaleX": 1,
                    "scaleY": 1,
                    "scaleZ": 1
                }
            })
            main_ids.append(card_id)
        card_id += 100

    # Process Egg Deck:
    egg_custom_deck = {}
    egg_cards = []
    egg_ids = []
    egg_card_id = 2000

    for card in egg_deck:
        count = card["count"]
        name = card["name"]
        code = card["code"]
        image_url = get_card_image_url(code)

        deck_index = str(egg_card_id // 100)
        if deck_index not in egg_custom_deck:
            egg_custom_deck[deck_index] = {
                "FaceURL": image_url,
                "BackURL": "https://static.wikia.nocookie.net/digimoncardgame/images/e/ef/Digi-Egg-Card-Back.png/revision/latest?cb=20210723050532",  # Egg deck back image
                "NumWidth": 1,
                "NumHeight": 1,
                "BackIsHidden": True
            }

        for _ in range(count):
            egg_cards.append({
                "Name": "Card",
                "Nickname": name,
                "CardID": egg_card_id,
                "Transform": {
                    "posX": 0,
                    "posY": 3,
                    "posZ": 0,
                    "rotX": 0,
                    "rotY": 180,
                    "rotZ": 180,
                    "scaleX": 1,
                    "scaleY": 1,
                    "scaleZ": 1
                }
            })
            egg_ids.append(egg_card_id)
        egg_card_id += 100

    # Create two separate deck objects (one for main and one for eggs)
    main_deck_object = {
        "Name": "Deck",
        "Nickname": deck_name,
        "ContainedObjects": main_cards,
        "DeckIDs": main_ids,
        "CustomDeck": main_custom_deck,
        "Transform": {
            "posX": 0,
            "posY": 3,
            "posZ": 0,
            "rotX": 0,
            "rotY": 180,
            "rotZ": 180,
            "scaleX": 1,
            "scaleY": 1,
            "scaleZ": 1
        }
    }

    egg_deck_object = {
        "Name": "Deck",
        "Nickname": "Egg Deck",
        "ContainedObjects": egg_cards,
        "DeckIDs": egg_ids,
        "CustomDeck": egg_custom_deck,
        "Transform": {
            "posX": 3,
            "posY": 3,
            "posZ": 0,
            "rotX": 0,
            "rotY": 180,
            "rotZ": 180,
            "scaleX": 1,
            "scaleY": 1,
            "scaleZ": 1
        }
    }

    # Final JSON file will have these two deck objects as top-level objects.
    object_states = [main_deck_object, egg_deck_object]
    
    # Return the JSON string that wraps our deck objects in "ObjectStates"
    return json.dumps({"ObjectStates": object_states}, indent=2)

# ----------- GUI Setup -----------
root = tk.Tk()
root.title("Digimon Deck JSON Compiler")
root.geometry("600x550")

# Label for Deck Name
deck_name_label = tk.Label(root, text="Enter Deck Name:", font=("Arial", 12))
deck_name_label.pack(pady=(10, 2))

# Entry field for Deck Name
deck_name_entry = tk.Entry(root, font=("Arial", 12), width=50)
deck_name_entry.pack(pady=5)

# Label for deck list input
label = tk.Label(root, text="Paste your Digimon Deck List below:", font=("Arial", 12))
label.pack(pady=10)

# Text box for deck input
deck_input = tk.Text(root, height=20, width=70)
deck_input.pack(pady=10)

# Button click handler
def compile_deck():
    deck_text = deck_input.get("1.0", tk.END).strip()
    deck_name = deck_name_entry.get().strip()

    if not deck_text:
        messagebox.showwarning("Missing deck list", "Please paste a deck list.")
        return

    if not deck_name:
        messagebox.showwarning("Missing Deck Name", "Please enter a name for your deck.")
        return

    # Parse the text into main and egg decks
    main_deck, egg_deck = parse_decklist(deck_text)

    # Build the TTS JSON object using the deck name;
    tts_deck_json = build_tts_deck(deck_name, main_deck, egg_deck)

    # Prompt for file save location
    save_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        initialfile=f"{deck_name}.json",
        title="Save TTS Deck As..."
    )
    
    if save_path:
        if os.path.exists(save_path):
            confirm = messagebox.askyesno("Overwrite File", "That file already exists. Overwrite?")
            if not confirm:
                return
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(tts_deck_json)
        messagebox.showinfo("Deck Exported", f"Deck saved as '{save_path}'!")

# Button to trigger compiling/export
import_button = tk.Button(root, text="Compile Deck", font=("Arial", 12), command=compile_deck)
import_button.pack(pady=20)

# Start the GUI loop
root.mainloop()