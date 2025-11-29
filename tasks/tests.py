from django.test import TestCase
from datetime import date, timedelta
from tasks.models import Task
from tasks.scoring import (
    calculate_urgency_score,
    calculate_importance_score,
    calculate_effort_score,
    calculate_dependency_score,
    calculate_priority_score,
    score_tasks
)


class ScoringAlgorithmTestCase(TestCase):
    """Test cases for the task priority scoring algorithm"""

    def test_overdue_task_gets_maximum_urgency(self):
        """Test that overdue tasks receive the maximum urgency score of 100"""
        # Create a task that's 5 days overdue
        overdue_task = Task(
            title="Overdue Task",
            due_date=date.today() - timedelta(days=5),
            estimated_hours=4,
            importance=7
        )
        
        urgency_score = calculate_urgency_score(overdue_task)
        
        # Overdue tasks should get maximum urgency score
        self.assertEqual(urgency_score, 100, 
                        "Overdue tasks should receive maximum urgency score of 100")

    def test_urgent_task_scores_higher_than_distant_task(self):
        """Test that tasks due soon score higher than tasks due in the distant future"""
        # Task due tomorrow
        urgent_task = Task(
            title="Urgent Task",
            due_date=date.today() + timedelta(days=1),
            estimated_hours=4,
            importance=5
        )
        
        # Task due in 30 days
        distant_task = Task(
            title="Distant Task",
            due_date=date.today() + timedelta(days=30),
            estimated_hours=4,
            importance=5
        )
        
        urgent_score = calculate_priority_score(urgent_task)
        distant_score = calculate_priority_score(distant_task)
        
        self.assertGreater(urgent_score, distant_score,
                          "Tasks due soon should have higher priority than distant tasks")

    def test_high_importance_task_scores_higher(self):
        """Test that high importance tasks score higher than low importance tasks"""
        # High importance task
        high_importance_task = Task(
            title="Critical Task",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=4,
            importance=10
        )
        
        # Low importance task
        low_importance_task = Task(
            title="Minor Task",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=4,
            importance=2
        )
        
        high_score = calculate_priority_score(high_importance_task)
        low_score = calculate_priority_score(low_importance_task)
        
        self.assertGreater(high_score, low_score,
                          "High importance tasks should score higher than low importance tasks")

    def test_quick_task_scores_higher_than_long_task(self):
        """Test that quick tasks (low effort) score higher than lengthy tasks"""
        # Quick 2-hour task
        quick_task = Task(
            title="Quick Task",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=2,
            importance=5
        )
        
        # Long 20-hour task
        long_task = Task(
            title="Long Task",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=20,
            importance=5
        )
        
        quick_score = calculate_priority_score(quick_task)
        long_score = calculate_priority_score(long_task)
        
        self.assertGreater(quick_score, long_score,
                          "Quick tasks should score higher than lengthy tasks (encouraging flow)")

    def test_effort_score_calculation(self):
        """Test that effort score correctly penalizes very long tasks"""
        # 1-hour task (should get high effort score of 50)
        quick_task = Task(
            title="1-hour task",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=1,
            importance=5
        )
        
        # 50-hour task (should get low effort score of 5)
        marathon_task = Task(
            title="50-hour task",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=50,
            importance=5
        )
        
        quick_effort = calculate_effort_score(quick_task)
        marathon_effort = calculate_effort_score(marathon_task)
        
        # Quick task should have much higher effort score
        self.assertGreater(quick_effort, marathon_effort,
                          "Short tasks should have higher effort scores")
        
        # Quick task should get 50 points
        self.assertEqual(quick_effort, 50.0,
                        "Tasks under 2 hours should get 50 effort points")
        
        # Marathon task should have very low effort score
        self.assertEqual(marathon_effort, 5.0,
                       "Very long tasks (>24 hours) should get 5 effort points")

    def test_tasks_with_dependencies_score_lower(self):
        """Test that tasks with dependencies receive lower priority scores"""
        # Task with no dependencies
        independent_task = Task(
            title="Independent Task",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=4,
            importance=5,
            dependencies=[]
        )
        
        # Task with 2 dependencies
        dependent_task = Task(
            title="Dependent Task",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=4,
            importance=5,
            dependencies=[1, 2]
        )
        
        independent_score = calculate_priority_score(independent_task)
        dependent_score = calculate_priority_score(dependent_task)
        
        self.assertGreater(independent_score, dependent_score,
                          "Tasks without dependencies should score higher")

    def test_score_tasks_returns_sorted_list(self):
        """Test that score_tasks returns tasks sorted by priority (highest first)"""
        tasks = [
            Task(
                id=1,
                title="Low Priority",
                due_date=date.today() + timedelta(days=30),
                estimated_hours=20,
                importance=2
            ),
            Task(
                id=2,
                title="High Priority",
                due_date=date.today() + timedelta(days=1),
                estimated_hours=2,
                importance=10
            ),
            Task(
                id=3,
                title="Medium Priority",
                due_date=date.today() + timedelta(days=7),
                estimated_hours=5,
                importance=5
            )
        ]
        
        scored_tasks = score_tasks(tasks)
        
        # Verify tasks are sorted by priority score (descending)
        for i in range(len(scored_tasks) - 1):
            self.assertGreaterEqual(
                scored_tasks[i].priority_score,
                scored_tasks[i + 1].priority_score,
                "Tasks should be sorted by priority score in descending order"
            )
        
        # The high priority task should be first
        self.assertEqual(scored_tasks[0].title, "High Priority",
                        "Highest priority task should be first in sorted list")

    def test_importance_score_scales_correctly(self):
        """Test that importance score scales from 0-100 based on importance level"""
        # Minimum importance (1)
        min_task = Task(
            title="Min Importance",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=4,
            importance=1
        )
        
        # Maximum importance (10)
        max_task = Task(
            title="Max Importance",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=4,
            importance=10
        )
        
        min_score = calculate_importance_score(min_task)
        max_score = calculate_importance_score(max_task)
        
        # Importance score should be 0-100
        self.assertGreaterEqual(min_score, 0, "Importance score should be >= 0")
        self.assertLessEqual(max_score, 100, "Importance score should be <= 100")
        
        # Max importance should give score of 100
        self.assertEqual(max_score, 100, "Importance 10 should give score of 100")
        
        # Min importance should give score of 10
        self.assertEqual(min_score, 10, "Importance 1 should give score of 10")

    def test_combined_score_reflects_all_factors(self):
        """Test that the final priority score considers all factors: urgency, importance, effort, dependencies"""
        # Perfect storm: overdue, high importance, quick, no dependencies
        perfect_task = Task(
            title="Perfect Priority Task",
            due_date=date.today() - timedelta(days=1),  # Overdue
            estimated_hours=1,  # Quick
            importance=10,  # Maximum importance
            dependencies=[]  # No dependencies
        )
        
        # Worst case: distant, low importance, lengthy, has dependencies
        worst_task = Task(
            title="Low Priority Task",
            due_date=date.today() + timedelta(days=60),  # Distant
            estimated_hours=40,  # Lengthy
            importance=1,  # Minimum importance
            dependencies=[1, 2, 3]  # Multiple dependencies
        )
        
        perfect_score = calculate_priority_score(perfect_task)
        worst_score = calculate_priority_score(worst_task)
        
        # Perfect task should have significantly higher score
        self.assertGreater(perfect_score, worst_score * 3,
                          "Perfect priority task should score much higher than worst case")
        
        # Perfect task should have very high score (close to maximum possible)
        self.assertGreater(perfect_score, 300,
                          "Perfect priority task should have very high score")
