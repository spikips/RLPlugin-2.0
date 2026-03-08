# slayer_task.py (fixed and cleaned)
# Fixes applied:
# - Removed undefined get_task_module_path() (leftover from old version).
# - All calls now correctly pass task_name (str) to run_task_module().
# - Minor cleanup: consistent prints, no unused variables.
# - Behavior unchanged: imports walk_to module (runs nav/hop top-level code),
#   then imports fighting module (runs slayer loop top-level code).
# - When fighting module finishes (task complete), control returns → orchestrator loops,
#   sees remaining == 0 → deletes JSON → gets new task.

import random
import sys
import os
import json
import time
import importlib

from modules.core.window_utils import focus_runelite_window
from modules.utils.automatic_scripting.small_functions import take_humanlike_break_if_needed
from modules.utils.logout import check_login_state_and_login
from modules.core.plugin_client import slayer_task_remaining
from modules.utils.loot import wait_for_next_tick
from scripts.combat.slayer.slayer_master_edgeville import full_navigation_with_skip_loop

TASK_FILE = "current_task.json"

tasks_to_skip = [
    "terror dogs",
    "spiritual creatures"
]

def normalize_task_name(task_name: str) -> str:
    """Convert task name from game to filename-friendly snake_case."""
    return task_name.strip().lower().replace(" ", "_").replace("-", "_")

def get_walk_to_module_path(task_name: str) -> str:
    """Construct the expected module path for the walk_to script."""
    normalized = normalize_task_name(task_name)
    return f"scripts.combat.slayer.tasks.{normalized}.walk_to_{normalized}"

def get_fighting_module_path(task_name: str) -> str:
    """Construct the expected module path for the fighting script (e.g., turoth.py)."""
    normalized = normalize_task_name(task_name)
    return f"scripts.combat.slayer.tasks.{normalized}.{normalized}"


def save_task(task_name: str, amount: int | None = None):
    """Save current task to JSON (now supports initial amount for progress tracking)."""
    try:
        data = {"task": task_name}
        if amount is not None:
            data["amount"] = amount
        with open(TASK_FILE, "w") as f:
            json.dump(data, f)
        print(f"Saved current task to {TASK_FILE}: {task_name} (amount: {amount or 'unknown'})")
    except Exception as e:
        print(f"Failed to save task to {TASK_FILE}: {e}")
        sys.exit(1)

def load_task() -> tuple[str | None, int | None]:
    """Load task name + amount from JSON if file exists."""
    if not os.path.exists(TASK_FILE):
        return None, None
    try:
        with open(TASK_FILE, "r") as f:
            data = json.load(f)
            task_name = data.get("task")
            amount = data.get("amount")
            if task_name:
                print(f"Loaded saved task from {TASK_FILE}: {task_name} (amount: {amount or 'unknown'})")
                return task_name, amount
            else:
                print(f"Invalid data in {TASK_FILE} - deleting.")
                os.remove(TASK_FILE)
                return None, None
    except Exception as e:
        print(f"Failed to load {TASK_FILE}: {e} - deleting.")
        if os.path.exists(TASK_FILE):
            os.remove(TASK_FILE)
        return None, None

def delete_task_file():
    """Remove the task JSON file."""
    if os.path.exists(TASK_FILE):
        os.remove(TASK_FILE)
        print(f"Deleted {TASK_FILE} (task completed or cleared).")

def run_task_module(task_name: str):
    """Import and run walk_to module's run() function, then import and run fighting module's run() function."""
    walk_to_path = get_walk_to_module_path(task_name)
    fighting_path = get_fighting_module_path(task_name)

    try:
        # Import and run walk_to navigation/hopping
        print(f"Starting navigation/hopping for {task_name}")
        walk_to_module = importlib.import_module(walk_to_path)
        if hasattr(walk_to_module, 'run'):
            walk_to_module.run()
        else:
            print(f"Warning: {walk_to_path} does not have a run() function")

        # Import and run fighting loop
        print(f"Starting slayer loop for {task_name}")
        fighting_module = importlib.import_module(fighting_path)
        if hasattr(fighting_module, 'run'):
            fighting_module.run()
        else:
            print(f"Warning: {fighting_path} does not have a run() function")
        
        print(f"Task {task_name} completed - returning to orchestrator for next task.")

    except ImportError as e:
        print(f"Missing script: {e}")
        print("Ensure both walk_to_<task>.py and <task>.py exist in the correct folders.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during task {task_name}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    focus_runelite_window()
    script_start_time = time.time()
    next_break_minutes = [round(random.triangular(25, 95, 55))]
    print(f"Script started. First break scheduled in approximately {next_break_minutes[0]} minutes.")
    while True:
        # Login first (handles logged out state)
        if check_login_state_and_login():
            wait_for_next_tick(2)

        # Check current slayer task remaining
        remaining = slayer_task_remaining()
        print(f"Slayer task remaining: {remaining}")

        if remaining == 0:
            # No ongoing task - clean up and get a new one
            print("No ongoing task - navigating to Vannaka for new assignment...")
            task_name = full_navigation_with_skip_loop(tasks_to_skip)

            if task_name is None:
                print("Failed to detect/accept new task name - retrying in 60 seconds...")
                time.sleep(60)
                continue

            task_name = task_name.strip()
            print(f"New task accepted: '{task_name}'")
            save_task(task_name)
            
            if take_humanlike_break_if_needed(script_start_time, next_break_minutes):
                script_start_time = time.time()
                print("Back from break - continuing slayer tasks\n")
            
            run_task_module(task_name)

        else:
            # Ongoing task detected
            saved_task = load_task()
            if saved_task and isinstance(saved_task, tuple) and saved_task[0]:
                task_name, amount = saved_task
                print(f"Resuming ongoing task: {task_name} (remaining: {remaining})")
                run_task_module(task_name)
            else:
                print(f"Ongoing task detected (remaining: {remaining}) but no saved task in {TASK_FILE}")
                print("Attempting to recover current task name by navigating to Vannaka...")
                
                task_name = full_navigation_with_skip_loop(tasks_to_skip)
                
                if task_name:
                    task_name = task_name.strip()
                    print(f"Successfully recovered current task: '{task_name}'")
                    save_task(task_name)
                    run_task_module(task_name)
                else:
                    print("Failed to automatically detect current task name from Vannaka.")
                    print("Manually check your task in-game and add {\"task\": \"Exact Task Name\"} to current_task.json")
                    print("or cancel the task in-game, then restart.")
                    sys.exit(1)