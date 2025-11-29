# 🎯 Smart Task Analyzer

A sophisticated web application that analyzes and prioritizes tasks based on urgency, importance, effort, and dependencies using a custom-built scoring algorithm.

## 📋 Table of Contents

- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Algorithm Explanation](#algorithm-explanation)
- [Design Decisions](#design-decisions)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Time Breakdown](#time-breakdown)
- [Future Improvements](#future-improvements)

## ✨ Features

- **Smart Priority Scoring**: Custom algorithm that weighs urgency, importance, effort, and dependencies
- **Multiple Sorting Strategies**: 
  - 🎯 Smart Priority (Recommended)
  - ⚡ Fastest Wins (Quick Tasks First)
  - 📅 Deadline Driven (Due Date First)
  - ⭐ Importance First
- **Large Task Recommendations**: Automatic suggestions to break down tasks >24 hours
- **Task Persistence**: LocalStorage integration for data persistence
- **Responsive UI**: Dark-themed, modern interface with color-coded priorities
- **JSON Import/Export**: Bulk task management support

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/imthiyagu07/smart-task-analyzer.git
   cd smart-task-analyzer
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser and navigate to: `http://localhost:8000`
   - The frontend is served from the `frontend/` directory

### Quick Start

1. Add tasks using the form on the left panel
2. Click "Analyze Tasks" to see prioritized results
3. Use the sort dropdown to try different prioritization strategies
4. Click "Suggest Tasks" to get top 3 recommendations for today

### Sample Test Data

Want to quickly test the application? Copy and paste this JSON into the "Load from JSON" section:

```json
{
    "tasks": [
        {
            "title": "Complete project report",
            "due_date": "2025-11-30",
            "estimated_hours": 3.0,
            "importance": 9,
            "dependencies": []
        },
        {
            "title": "Team meeting",
            "due_date": "2025-11-29",
            "estimated_hours": 1.0,
            "importance": 5,
            "dependencies": []
        },
        {
            "title": "Code review",
            "due_date": "2025-12-05",
            "estimated_hours": 2.0,
            "importance": 7,
            "dependencies": []
        },
        {
            "title": "Fix critical bug",
            "due_date": "2025-11-28",
            "estimated_hours": 4.0,
            "importance": 10,
            "dependencies": []
        },
        {
            "title": "Update documentation",
            "due_date": "2025-12-10",
            "estimated_hours": 1.5,
            "importance": 4,
            "dependencies": []
        },
        {
            "title": "Build a e-commerce application",
            "due_date": "2025-12-01",
            "estimated_hours": 30,
            "importance": 9,
            "dependencies": []
        }
    ]
}
```

**What to expect:**
- The **"Fix critical bug"** task should rank highest (overdue + max importance)
- The **"Build a e-commerce application"** task will show a recommendation to break it down (>24 hours)
- Try different sorting strategies to see how priorities change
- The **"Team meeting"** should rank high due to urgency (due today)

## 🧮 Algorithm Explanation

The Smart Task Analyzer uses a **multi-factor weighted scoring system** to calculate priority scores for each task. The algorithm considers four key dimensions:

### 1. **Urgency Score (0-100 points)**
Tasks are scored based on how soon they're due:
- **Overdue tasks**: Receive maximum urgency (100 points) to ensure immediate attention
- **Due today/tomorrow**: Get very high urgency (90-100 points)
- **Future tasks**: Use exponential decay formula: `100 / (1 + days_until_due)^0.7`

This exponential approach ensures that tasks due in 2 days get significantly higher priority than tasks due in 30 days, creating a natural urgency gradient.

### 2. **Importance Score (10-100 points)**
User-defined importance (1-10 scale) is linearly mapped to a 10-100 point range. This allows users to explicitly mark critical tasks that should rise to the top regardless of deadline.

### 3. **Effort Score (5-50 points)**
The algorithm **rewards quick wins** to maintain productivity flow:
- **Quick tasks (<2 hours)**: 50 points - Encourages momentum
- **Medium tasks (2-8 hours)**: 30 points - Balanced effort
- **Long tasks (8-24 hours)**: 15 points - Requires planning
- **Very long tasks (>24 hours)**: 5 points - Should be broken down

This tiered system naturally surfaces bite-sized tasks that can be completed quickly, while flagging marathon tasks that need decomposition.

### 4. **Dependency Score (0-100 points)**
Tasks with dependencies receive penalties:
- **No dependencies**: 100 points (ready to start)
- **With dependencies**: `100 / (1 + dependency_count)^0.5`

This ensures that blocked tasks don't clog the top of your priority list.

### Final Priority Score
The four components are weighted and summed:
```
Priority = (Urgency × 1.2) + (Importance × 1.0) + (Effort × 0.8) + (Dependency × 0.5)
```

**Weights rationale:**
- Urgency (1.2x): Deadlines are critical and non-negotiable
- Importance (1.0x): User judgment is valuable but balanced
- Effort (0.8x): Flow matters, but not more than deadlines
- Dependencies (0.5x): Blockers matter, but shouldn't dominate

This produces scores typically ranging from 50-400, with higher scores indicating higher priority. The algorithm naturally balances competing factors: a very important but distant task might score similarly to an urgent but less important task.

## 🎨 Design Decisions

### Architecture Choices

**1. Django Backend + Vanilla JavaScript Frontend**
- **Trade-off**: Chose simplicity over framework complexity
- **Why**: For this scope, a full React/Vue setup would be overkill. Vanilla JS keeps the bundle small and the code transparent
- **Benefit**: Zero build step, instant page loads, easy to understand and modify

**2. LocalStorage for Persistence**
- **Trade-off**: Client-side storage vs. database persistence
- **Why**: Tasks are analyzed on-demand, no need for server-side storage
- **Benefit**: Works offline, no authentication needed, instant load times
- **Limitation**: Data is browser-specific (acceptable for personal productivity tool)

**3. Stateless API Design**
- **Trade-off**: Stateless vs. session-based
- **Why**: Each analysis is independent, no user accounts needed
- **Benefit**: Scales easily, no session management overhead, RESTful principles

### Algorithm Design

**4. Exponential Decay for Urgency**
- **Trade-off**: Linear vs. exponential time decay
- **Why**: Linear decay doesn't capture the psychological urgency of near-term deadlines
- **Benefit**: Tasks due in 2 days feel 3x more urgent than tasks due in 10 days (matches human perception)

**5. Tiered Effort Scoring**
- **Trade-off**: Continuous vs. discrete effort buckets
- **Why**: Discrete tiers are more predictable and easier to reason about
- **Benefit**: Clear incentive structure: "Keep tasks under 2 hours for maximum flow"

**6. Large Task Recommendations (>24 hours)**
- **Trade-off**: Hard limits vs. soft suggestions
- **Why**: Don't want to reject valid tasks, but want to guide better behavior
- **Benefit**: Educational without being restrictive

### UI/UX Decisions

**7. Color-Coded Priority Levels**
- **Red (High)**: Score >200
- **Orange (Medium)**: Score 150-200
- **Green (Low)**: Score <150
- **Why**: Instant visual feedback, reduces cognitive load

**8. Multiple Sorting Strategies**
- **Trade-off**: Single "best" algorithm vs. user choice
- **Why**: Different contexts need different prioritization (deadline crunch vs. strategic planning)
- **Benefit**: Flexibility for different work styles and situations

**9. Dark Theme**
- **Why**: Reduces eye strain for extended use, modern aesthetic
- **Benefit**: Better for focus-intensive work sessions

## 📡 API Documentation

### POST `/api/tasks/analyze/`

Analyzes and prioritizes a list of tasks.

**Request Body:**
```json
{
  "tasks": [
    {
      "title": "Complete project proposal",
      "due_date": "2025-12-01",
      "estimated_hours": 4,
      "importance": 8,
      "dependencies": []
    }
  ],
  "sort_by": "priority"  // Options: "priority", "fastest_wins", "deadline", "importance"
}
```

**Response:**
```json
{
  "status": "success",
  "count": 1,
  "tasks": [
    {
      "title": "Complete project proposal",
      "due_date": "2025-12-01",
      "estimated_hours": 4,
      "importance": 8,
      "dependencies": [],
      "priority_score": 245.6,
      "days_until_due": 2,
      "is_overdue": false,
      "recommendation": null
    }
  ]
}
```

### POST `/api/tasks/suggest/`

Returns top 3 task recommendations with explanations.

**Request Body:**
```json
{
  "tasks": [/* array of tasks */]
}
```

**Response:**
```json
{
  "status": "success",
  "suggestions": [
    {
      "task": {/* task object */},
      "explanation": "High priority due to approaching deadline and high importance"
    }
  ]
}
```

## 🧪 Testing

The project includes comprehensive unit tests for the scoring algorithm.

**Run all tests:**
```bash
python manage.py test tasks.tests.ScoringAlgorithmTestCase
```

**Run with verbose output:**
```bash
python manage.py test tasks.tests.ScoringAlgorithmTestCase -v 2
```

**Test Coverage:**
- ✅ Urgency scoring (overdue, near-term, distant tasks)
- ✅ Importance scaling (1-10 → 10-100 points)
- ✅ Effort scoring (quick wins vs. marathon tasks)
- ✅ Dependency penalties
- ✅ Combined scoring with edge cases
- ✅ Task sorting and ranking

**Total: 10 unit tests** covering all scoring components and integration scenarios.

## ⏱️ Time Breakdown

**Total Development Time: ~8-10 hours**

| Phase | Time Spent | Details |
|-------|------------|---------|
| **Planning & Design** | 1 hour | Algorithm design, architecture decisions, UI mockups |
| **Backend Development** | 2.5 hours | Django setup, models, scoring algorithm, API endpoints |
| **Frontend Development** | 2.5 hours | HTML structure, CSS styling, JavaScript logic, localStorage |
| **Algorithm Refinement** | 1.5 hours | Testing different weight combinations, edge case handling |
| **Testing** | 1 hour | Writing unit tests, manual testing, bug fixes |
| **Documentation** | 1 hour | README, code comments, API documentation |
| **Polish & Features** | 0.5 hours | Large task recommendations, color coding, sorting strategies |

## 🚀 Future Improvements

### High Priority (Next Sprint)

1. **Task Dependencies Visualization**
   - Implement a dependency graph view
   - Show which tasks are blocking others
   - Auto-suggest optimal task order based on dependency chains

2. **User Accounts & Cloud Sync**
   - Add authentication system
   - Store tasks in database
   - Sync across devices
   - Share task lists with team members

3. **Advanced Analytics**
   - Task completion tracking
   - Productivity metrics (tasks completed per day)
   - Time estimation accuracy (estimated vs. actual)
   - Burndown charts for project tracking

### Medium Priority

4. **Recurring Tasks**
   - Support for daily/weekly/monthly tasks
   - Auto-regenerate tasks after completion
   - Smart scheduling based on historical patterns

5. **Calendar Integration**
   - Sync with Google Calendar / Outlook
   - Block time for high-priority tasks
   - Deadline conflict detection

6. **Smart Notifications**
   - Email/push notifications for overdue tasks
   - Daily digest of top priorities
   - Deadline reminders (1 day, 1 week before)

7. **Mobile App**
   - Native iOS/Android apps
   - Offline-first architecture
   - Quick task capture with voice input

### Low Priority (Nice to Have)

8. **AI-Powered Suggestions**
   - Use ML to learn user preferences
   - Predict task duration based on historical data
   - Auto-categorize tasks by type

9. **Team Collaboration**
   - Assign tasks to team members
   - Shared priority queues
   - Comment threads on tasks

10. **Integrations**
    - Jira/Asana/Trello import
    - Slack bot for task management
    - GitHub issue sync

11. **Customizable Scoring**
    - Let users adjust algorithm weights
    - Create custom scoring profiles (e.g., "Deadline Mode", "Flow State")
    - A/B test different algorithms

12. **Gamification**
    - Streak tracking for daily task completion
    - Achievement badges
    - Leaderboards for team productivity

## 👤 Author

**Imthiyagu**
- GitHub: [@imthiyagu07](https://github.com/imthiyagu07)


**Built with ❤️ and ☕ by Imthiyagu**
