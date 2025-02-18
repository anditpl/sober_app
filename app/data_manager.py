"""
Module: data_manager
Handles loading and saving data stored in a JSON file.
"""

import json
import os

DATA_FILE = "sober_data.json"

def load_data() -> dict:
    """
    Loads data from the JSON file. If the file does not exist,
    returns a default data structure.

    Returns:
        dict: Data loaded from file.
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
    except Exception as e:
        print(f"Error loading data: {e}")
        data = {}
    data.setdefault("daily_drink_cost", 0.0)  # Set manually if needed
    data.setdefault("daily_log", {})
    return data

def save_data(data: dict) -> None:
    """
    Saves the provided data dictionary to the JSON file.

    Parameters:
        data (dict): The data to save.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")
