import json
import os
from datetime import datetime

# File path for storing goals
GOALS_FILE = "saved_goals.json"

def load_goals():
    """Load saved goals from the JSON file"""
    if not os.path.exists(GOALS_FILE):
        return []
    
    try:
        with open(GOALS_FILE, 'r') as f:
            goals = json.load(f)
            # For demo mode, ensure we only return the first goal if multiple exist
            if isinstance(goals, list) and len(goals) > 0:
                return [goals[0]]
            return goals
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted or doesn't exist, return empty list
        return []

def save_goal(goal_data, overwrite=False):
    """Save a goal to the storage file
    
    Args:
        goal_data: The goal data to save
        overwrite: If True, replace any existing goals with this one
    """
    if overwrite:
        # In demo mode, we only keep one goal - just overwrite the file
        goal_data["id"] = 1  # Always use ID 1
        goals = [goal_data]
    else:
        goals = load_goals()
        
        # Add timestamp and unique ID if not already present
        if "created_at" not in goal_data:
            goal_data["created_at"] = datetime.now().isoformat()
        if "id" not in goal_data:
            goal_data["id"] = 1 if not goals else goals[0].get("id", 1)
        
        # In demo mode, replace the existing goal if any
        if goals:
            goals[0] = goal_data
        else:
            goals.append(goal_data)
    
    # Save to file
    with open(GOALS_FILE, 'w') as f:
        json.dump(goals, f, indent=2)
    
    return goal_data

def get_latest_goal():
    """Get the most recently created goal"""
    goals = load_goals()
    if not goals:
        return None
    
    # In demo mode, just return the only goal
    return goals[0]

def delete_goal(goal_id):
    """Delete the goal (in demo mode, this clears the file)"""
    # In demo mode, we just delete the file or create an empty goals list
    with open(GOALS_FILE, 'w') as f:
        json.dump([], f, indent=2)
    
    return True 