from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date
import json
from datetime import datetime

from .models import Task
from .scoring import calculate_priority_score, score_tasks, get_top_tasks_for_today


@csrf_exempt
@require_http_methods(["POST"])
def analyze_tasks(request):
    try:
        # Parse request body
        data = json.loads(request.body)
        tasks_data = data.get('tasks', [])
        sort_by = data.get('sort_by', 'priority')
        
        if not tasks_data:
            return JsonResponse({
                'status': 'error',
                'message': 'No tasks provided'
            }, status=400)
        
        # Create temporary Task objects (not saved to database)
        tasks = []
        for idx, task_data in enumerate(tasks_data):
            try:
                # Validate required fields
                if not all(k in task_data for k in ['title', 'due_date', 'estimated_hours', 'importance']):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Task {idx + 1} is missing required fields'
                    }, status=400)
                
                # Parse due_date
                due_date = parse_date(task_data['due_date'])
                if not due_date:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Task {idx + 1} has invalid due_date format. Use YYYY-MM-DD'
                    }, status=400)
                
                # Validate importance range
                importance = int(task_data['importance'])
                if importance < 1 or importance > 10:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Task {idx + 1} importance must be between 1 and 10'
                    }, status=400)
                
                # Validate estimated_hours
                estimated_hours = float(task_data['estimated_hours'])
                if estimated_hours < 0.1:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Task {idx + 1} estimated_hours must be at least 0.1'
                    }, status=400)
                
                # Create task object
                task = Task(
                    id=idx + 1,  # Temporary ID for dependency tracking
                    title=task_data['title'],
                    due_date=due_date,
                    estimated_hours=estimated_hours,
                    importance=importance,
                    dependencies=task_data.get('dependencies', [])
                )
                tasks.append(task)
                
            except (ValueError, TypeError) as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Task {idx + 1} has invalid data: {str(e)}'
                }, status=400)
        
        # Score all tasks
        scored_tasks = score_tasks(tasks)
        
        # Apply sorting strategy
        if sort_by == 'due_date':
            scored_tasks.sort(key=lambda t: t.due_date)
        elif sort_by == 'importance':
            scored_tasks.sort(key=lambda t: t.importance, reverse=True)
        # else: already sorted by priority from score_tasks()
        
        # Build response
        response_tasks = []
        for task in scored_tasks:
            response_tasks.append({
                'title': task.title,
                'due_date': task.due_date.isoformat(),
                'estimated_hours': task.estimated_hours,
                'importance': task.importance,
                'dependencies': task.dependencies,
                'priority_score': task.priority_score,
                'days_until_due': task.days_until_due(),
                'is_overdue': task.is_overdue()
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(response_tasks),
            'tasks': response_tasks
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def suggest_tasks(request):
    try:
        # Parse request body
        data = json.loads(request.body)
        tasks_data = data.get('tasks', [])
        
        if not tasks_data:
            return JsonResponse({
                'status': 'error',
                'message': 'No tasks provided'
            }, status=400)
        
        # Create temporary Task objects
        tasks = []
        for idx, task_data in enumerate(tasks_data):
            try:
                due_date = parse_date(task_data['due_date'])
                
                task = Task(
                    id=idx + 1,
                    title=task_data['title'],
                    due_date=due_date,
                    estimated_hours=float(task_data['estimated_hours']),
                    importance=int(task_data['importance']),
                    dependencies=task_data.get('dependencies', [])
                )
                tasks.append(task)
                
            except (ValueError, TypeError, KeyError) as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Task {idx + 1} has invalid data: {str(e)}'
                }, status=400)
        
        # Get top 3 tasks with explanations
        top_tasks = get_top_tasks_for_today(tasks, limit=3)
        
        # Build response
        suggestions = []
        for task, explanation in top_tasks:
            suggestions.append({
                'task': {
                    'title': task.title,
                    'due_date': task.due_date.isoformat(),
                    'estimated_hours': task.estimated_hours,
                    'importance': task.importance,
                    'priority_score': task.priority_score,
                    'days_until_due': task.days_until_due()
                },
                'explanation': explanation
            })
        
        return JsonResponse({
            'status': 'success',
            'suggestions': suggestions
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)