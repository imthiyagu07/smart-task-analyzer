from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Task(models.Model):
    """
    Model representing a task with priority scoring capabilities.
    """
    title = models.CharField(
        max_length=200,
        help_text="Task title or description"
    )
    
    due_date = models.DateField(
        help_text="When the task is due"
    )
    
    estimated_hours = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Estimated hours to complete the task"
    )
    
    importance = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        help_text="Importance level from 1 (low) to 10 (high)"
    )
    
    dependencies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of task IDs that this task depends on"
    )
    
    priority_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Calculated priority score (higher = more urgent)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the task was created"
    )
    
    class Meta:
        ordering = ['-priority_score', 'due_date']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
    
    def __str__(self):
        return f"{self.title} (Due: {self.due_date})"
    
    def is_overdue(self):
        """Check if the task is past its due date."""
        return self.due_date < timezone.now().date()
    
    def days_until_due(self):
        """Calculate how many days until the task is due."""
        delta = self.due_date - timezone.now().date()
        return delta.days