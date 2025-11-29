from datetime import datetime, date
from django.utils import timezone
import math


def calculate_urgency_score(task):
    days_until_due = task.days_until_due()
    
    # Overdue tasks get maximum urgency
    if days_until_due < 0:
        return 100.0
    
    # Due today gets maximum urgency
    if days_until_due == 0:
        return 100.0
    
    # Due tomorrow gets very high urgency
    if days_until_due == 1:
        return 90.0
    
    # For future tasks use exponential decay
    urgency = 100 / math.pow(1 + days_until_due, 0.7)
    
    return round(urgency, 2)


def calculate_importance_score(task):
    return task.importance * 10.0


def calculate_effort_score(task):
    hours = task.estimated_hours
    
    # Quick tasks (< 2 hours) get a bonus
    if hours <= 2:
        return 50.0
    
    # Medium tasks (2-8 hours) get moderate scores
    if hours <= 8:
        return 30.0
    
    # Long tasks (8-24 hours) get lower scores
    if hours <= 24:
        return 15.0
    
    # Very long tasks get minimal effort score
    return 5.0


def calculate_dependency_score(task, all_tasks=None):
    if all_tasks is None:
        return 0.0
    
    # Count how many tasks list this task as a dependency
    blocked_count = 0
    
    for other_task in all_tasks:
        # Skip the task itself
        if other_task.id == task.id:
            continue
        
        # Check if this task is in the other task's dependencies
        if task.id in other_task.dependencies:
            blocked_count += 1
    
    # Each blocked task adds 15 points (max 50)
    dependency_score = min(blocked_count * 15, 50.0)
    
    return dependency_score


def calculate_priority_score(task, all_tasks=None):
    # Calculate individual components
    urgency = calculate_urgency_score(task)
    importance = calculate_importance_score(task)
    effort = calculate_effort_score(task)
    dependencies = calculate_dependency_score(task, all_tasks)
    
    # Weighted combination
    # Urgency and importance are most critical
    score = (urgency * 1.2 + importance * 1.0 + effort * 0.5 + dependencies * 0.3)
    
    return round(score, 2)


def score_tasks(tasks):
    # Calculate scores for all tasks
    for task in tasks:
        task.priority_score = calculate_priority_score(task, tasks)
    
    # Sort by priority score (descending)
    sorted_tasks = sorted(tasks, key=lambda t: t.priority_score, reverse=True)
    
    return sorted_tasks


def get_top_tasks_for_today(tasks, limit=3):
    # Score all tasks
    scored_tasks = score_tasks(tasks)
    
    # Get top N tasks
    top_tasks = scored_tasks[:limit]
    
    # Generate explanations
    results = []
    for task in top_tasks:
        explanation = generate_task_explanation(task)
        results.append((task, explanation))
    
    return results


def generate_task_explanation(task):
    reasons = []
    
    # Check urgency
    days = task.days_until_due()
    if days < 0:
        reasons.append(f"⚠️ OVERDUE by {abs(days)} day(s)")
    elif days == 0:
        reasons.append("🔥 Due TODAY")
    elif days == 1:
        reasons.append("⏰ Due TOMORROW")
    elif days <= 3:
        reasons.append(f"📅 Due in {days} days")
    
    # Check importance
    if task.importance >= 8:
        reasons.append(f"⭐ High importance ({task.importance}/10)")
    elif task.importance >= 5:
        reasons.append(f"📌 Medium importance ({task.importance}/10)")
    
    # Check effort
    if task.estimated_hours <= 2:
        reasons.append(f"✅ Quick task ({task.estimated_hours}h)")
    elif task.estimated_hours >= 16:
        reasons.append(f"🏗️ Large project ({task.estimated_hours}h)")
    
    # Combine reasons
    if reasons:
        return " • ".join(reasons)
    else:
        return "Standard priority task"