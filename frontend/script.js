// API Base URL
const API_BASE = 'http://localhost:8000/api/tasks';

// Task storage
let tasks = [];

// Load tasks from localStorage on page load
function loadTasksFromStorage() {
    const savedTasks = localStorage.getItem('taskAnalyzerTasks');
    if (savedTasks) {
        try {
            tasks = JSON.parse(savedTasks);
        } catch (error) {
            console.error('Error loading tasks from localStorage:', error);
            tasks = [];
        }
    }
}

// Save tasks to localStorage
function saveTasksToStorage() {
    try {
        localStorage.setItem('taskAnalyzerTasks', JSON.stringify(tasks));
    } catch (error) {
        console.error('Error saving tasks to localStorage:', error);
    }
}

// Add task from form
function addTask() {
    const title = document.getElementById('taskTitle').value.trim();
    const dueDate = document.getElementById('taskDueDate').value;
    const hours = parseFloat(document.getElementById('taskHours').value);
    const importance = parseInt(document.getElementById('taskImportance').value);

    // Validation
    if (!title || !dueDate || !hours || !importance) {
        alert('Please fill in all fields');
        return;
    }

    if (importance < 1 || importance > 10) {
        alert('Importance must be between 1 and 10');
        return;
    }

    if (hours < 0.1) {
        alert('Hours must be at least 0.1');
        return;
    }

    // Add task
    const task = {
        title,
        due_date: dueDate,
        estimated_hours: hours,
        importance,
        dependencies: []
    };

    tasks.push(task);

    // Save to localStorage
    saveTasksToStorage();

    // Clear form
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDueDate').value = '';
    document.getElementById('taskHours').value = '';
    document.getElementById('taskImportance').value = '';

    // Update display
    displayTaskList();
}

// Display task list
function displayTaskList() {
    const taskList = document.getElementById('taskList');

    if (tasks.length === 0) {
        taskList.innerHTML = '<p style="text-align: center; color: #999;">No tasks added yet</p>';
        return;
    }

    taskList.innerHTML = tasks.map((task, index) => `
        <div class="task-item">
            <div class="task-info">
                <strong>${task.title}</strong>
                <div class="task-meta">
                    Due: ${task.due_date} | ${task.estimated_hours}h | Importance: ${task.importance}/10
                </div>
            </div>
            <button class="task-remove" onclick="removeTask(${index})">Remove</button>
        </div>
    `).join('');
}

// Remove task
function removeTask(index) {
    tasks.splice(index, 1);
    saveTasksToStorage();
    displayTaskList();
}

// Load from JSON
function loadFromJSON() {
    const jsonInput = document.getElementById('jsonInput').value.trim();

    if (!jsonInput) {
        alert('Please paste JSON data');
        return;
    }

    try {
        const data = JSON.parse(jsonInput);
        if (data.tasks && Array.isArray(data.tasks)) {
            tasks = data.tasks;
            saveTasksToStorage();
            displayTaskList();
            alert(`Loaded ${tasks.length} tasks successfully!`);
        } else {
            alert('Invalid JSON format. Expected {"tasks": [...]}');
        }
    } catch (error) {
        alert('Invalid JSON: ' + error.message);
    }
}

// Analyze tasks
async function analyzeTasks() {
    if (tasks.length === 0) {
        alert('Please add some tasks first');
        return;
    }

    const sortBy = document.getElementById('sortStrategy').value;
    const resultsDiv = document.getElementById('results');

    resultsDiv.innerHTML = '<p class="placeholder">Analyzing tasks...</p>';

    try {
        const response = await fetch(`${API_BASE}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                sort_by: sortBy
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            displayResults(data.tasks);
        } else {
            resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.message}</p>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p style="color: red;">Error connecting to server: ${error.message}</p>`;
    }
}

// Display results
function displayResults(analyzedTasks) {
    const resultsDiv = document.getElementById('results');

    resultsDiv.innerHTML = analyzedTasks.map(task => {
        const priorityClass = task.priority_score > 200 ? 'priority-high' :
            task.priority_score > 150 ? 'priority-medium' : 'priority-low';

        const overdueTag = task.is_overdue ? '<span style="color: red; font-weight: bold;">⚠️ OVERDUE</span>' : '';
        const recommendationHtml = task.recommendation ? `<div class="recommendation-tip">${task.recommendation}</div>` : '';

        return `
            <div class="result-card ${priorityClass}">
                <div class="result-title">
                    ${task.title}
                    <span class="result-score">Score: ${task.priority_score}</span>
                </div>
                ${overdueTag}
                ${recommendationHtml}
                <div class="result-details">
                    <div class="result-detail"><strong>Due:</strong> ${task.due_date}</div>
                    <div class="result-detail"><strong>Days until due:</strong> ${task.days_until_due}</div>
                    <div class="result-detail"><strong>Hours:</strong> ${task.estimated_hours}h</div>
                    <div class="result-detail"><strong>Importance:</strong> ${task.importance}/10</div>
                </div>
            </div>
        `;
    }).join('');
}

// Get suggestions
async function getSuggestions() {
    if (tasks.length === 0) {
        alert('Please add some tasks first');
        return;
    }

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p class="placeholder">Getting top suggestions...</p>';

    try {
        const response = await fetch(`${API_BASE}/suggest/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            displaySuggestions(data.suggestions);
        } else {
            resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.message}</p>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p style="color: red;">Error connecting to server: ${error.message}</p>`;
    }
}

// Display suggestions
function displaySuggestions(suggestions) {
    const resultsDiv = document.getElementById('results');

    resultsDiv.innerHTML = '<h3 style="margin-bottom: 20px; color: white;">🌟 Top 3 Tasks for Today</h3>' +
        suggestions.map((item, index) => {
            const task = item.task;
            return `
                <div class="suggestion-card">
                    <div class="result-title">
                        <span class="suggestion-rank">${index + 1}</span>
                        ${task.title}
                        <span class="result-score">Score: ${task.priority_score}</span>
                    </div>
                    <div class="result-explanation">
                        ${item.explanation}
                    </div>
                    <div class="result-details">
                        <div class="result-detail"><strong>Due:</strong> ${task.due_date}</div>
                        <div class="result-detail"><strong>Days until due:</strong> ${task.days_until_due}</div>
                        <div class="result-detail"><strong>Hours:</strong> ${task.estimated_hours}h</div>
                        <div class="result-detail"><strong>Importance:</strong> ${task.importance}/10</div>
                    </div>
                </div>
            `;
        }).join('');
}

// Clear all
function clearAll() {
    if (confirm('Are you sure you want to clear all tasks?')) {
        tasks = [];
        saveTasksToStorage();
        displayTaskList();
        document.getElementById('results').innerHTML = '<p class="placeholder">Add tasks and click "Analyze" to see prioritized results</p>';
    }
}

// Initialize - Load tasks from localStorage and display
loadTasksFromStorage();
displayTaskList();

// Add event listener for sort strategy change
document.getElementById('sortStrategy').addEventListener('change', () => {
    if (tasks.length > 0) {
        analyzeTasks();
    }
});