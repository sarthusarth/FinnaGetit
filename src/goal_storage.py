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
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted or doesn't exist, return empty list
        return []

def save_goal(goal_data):
    """Save a new goal to the storage file"""
    goals = load_goals()
    
    # Add timestamp and unique ID
    goal_data["created_at"] = datetime.now().isoformat()
    goal_data["id"] = len(goals) + 1
    
    # Add to goals list
    goals.append(goal_data)
    
    # Save back to file
    with open(GOALS_FILE, 'w') as f:
        json.dump(goals, f, indent=2)
    
    return goal_data

def get_latest_goal():
    """Get the most recently created goal"""
    goals = load_goals()
    if not goals:
        return None
    
    # Sort by created_at and return the latest
    return sorted(goals, key=lambda x: x.get("created_at", ""), reverse=True)[0]

def delete_goal(goal_id):
    """Delete a goal by its ID"""
    goals = load_goals()
    goals = [g for g in goals if g.get("id") != goal_id]
    
    with open(GOALS_FILE, 'w') as f:
        json.dump(goals, f, indent=2)
    
    return True 