# slayer_task.py
# Fully automatic Slayer task orchestrator with crash recovery via current_task.json
# - Dynamically loads task module based on saved task name (for recovery) or newly assigned.
# - Saves current task to current_task.json when a new task is successfully assigned.
# - On startup/recovery: Checks slayer_task_remaining() after login.
#   - If remaining == 0 → delete any old JSON → get new task → save → run.
#   - If remaining > 0 → use saved task from JSON (if exists) → run module.
#     If no saved task but remaining > 0 → exit with error (manual fix needed).
# - Strict exit on any problem (unsupported task, missing main(), exceptions).

import sys
import os
import json
import time
import importlib

from modules.core.window_utils import focus_runelite_window
from modules.utils.logout import check_login_state_and_login, logout
from modules.core.plugin_client import slayer_task_remaining
from modules.utils.loot import wait_for_next_tick
from scripts.combat.slayer.walk_to.slayer_master_edgeville import full_navigation

TASK_FILE = "current_task.json"

def normalize_task_name(task_name: str) -> str:
    """Convert task name from game to filename-friendly snake_case."""
    return task_name.strip().lower().replace(" ", "_").replace("-", "_")

def get_task_module_path(task_name: str) -> str:
    """Construct the expected module path for the walk_to script."""
    normalized = normalize_task_name(task_name)
    return f"scripts.combat.slayer.walk_to.walk_to_{normalized}"

def save_task(task_name: str):
    """Save the current task to JSON."""
    try:
        with open(TASK_FILE, "w") as f:
            json.dump({"task": task_name}, f)
        print(f"Saved current task to {TASK_FILE}: {task_name}")
    except Exception as e:
        print(f"Failed to save task to {TASK_FILE}: {e}")
        sys.exit(1)

def load_task() -> str | None:
    """Load task name from JSON if file exists."""
    if not os.path.exists(TASK_FILE):
        return None
    try:
        with open(TASK_FILE, "r") as f:
            data = json.load(f)
            task_name = data.get("task")
            if task_name:
                print(f"Loaded saved task from {TASK_FILE}: {task_name}")
                return task_name
            else:
                print(f"Invalid data in {TASK_FILE} - deleting.")
                os.remove(TASK_FILE)
                return None
    except Exception as e:
        print(f"Failed to load {TASK_FILE}: {e} - deleting.")
        if os.path.exists(TASK_FILE):
            os.remove(TASK_FILE)
        return None

def delete_task_file():
    """Remove the task JSON file."""
    if os.path.exists(TASK_FILE):
        os.remove(TASK_FILE)
        print(f"Deleted {TASK_FILE} (task completed or cleared).")

def run_task_module(module_path: str):
    """Dynamically import and run the main() of the task module. Exits on any issue."""
    try:
        module = importlib.import_module(module_path)
        if not hasattr(module, "main"):
            print(f"Error: Module {module_path} has no main() function - exiting.")
            sys.exit(1)
        print(f"Starting automated task: {module_path}")
        module.main()
        print(f"Task module {module_path} completed successfully.")
    except ImportError:
        print(f"Unsupported task - no walk_to file found for module '{module_path}'.")
        print("Add the corresponding walk_to_<task>.py file and restart the script.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error while running task module {module_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    focus_runelite_window()
    while True:
        # Login first (handles logged out state)
        if check_login_state_and_login():
            wait_for_next_tick(2)

        # Check current slayer task remaining
        remaining = slayer_task_remaining()
        print(f"Slayer task remaining: {remaining}")

        if remaining == 0:
            # No ongoing task - clean up and get a new one
            delete_task_file()
            print("No ongoing task - navigating to Vannaka for new assignment...")
            task_name = full_navigation()  # This logs out at the end

            if task_name is None:
                print("Failed to detect new task name - retrying in 60 seconds...")
                exit()

            task_name = task_name.strip()
            print(f"New task assigned: '{task_name}'")
            save_task(task_name)

            module_path = get_task_module_path(task_name)
            run_task_module(module_path)

        else:
            # Ongoing task detected
            saved_task = load_task()
            if saved_task:
                print(f"Resuming ongoing task: {saved_task} (remaining: {remaining})")
                module_path = get_task_module_path(saved_task)
                run_task_module(module_path)
            else:
                # Ongoing task but no saved task in JSON - recover by talking to Vannaka
                print(f"Ongoing task detected (remaining: {remaining}) but no saved task in {TASK_FILE}")
                print("Attempting to recover current task name by navigating to Vannaka...")
                
                task_name = full_navigation()  # Teleport → go to Vannaka → click "Assignment" (shows reminder text)
                
                if task_name:
                    task_name = task_name.strip()
                    print(f"Successfully recovered current task: '{task_name}'")
                    save_task(task_name)
                    
                    module_path = get_task_module_path(task_name)
                    run_task_module(module_path)
                else:
                    print("Failed to automatically detect current task name from Vannaka.")
                    print("Manually check your task in-game and add {\"task\": \"Exact Task Name\"} to current_task.json")
                    print("or cancel the task in-game, then restart.")
                    sys.exit(1)