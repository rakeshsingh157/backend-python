# AI Generate Schedule API Documentation

## Endpoint
`POST /api/{user_id}/ai/generate-schedule`

## Description
AI-powered schedule generation endpoint that creates comprehensive task lists from natural language prompts. **The AI automatically generates intelligent reminder settings based on task type, category, and importance level.**

## Features
- 🤖 **Natural Language Processing**: Understands complex scheduling requests
- 🧠 **Intelligent Reminder Generation**: Automatically sets appropriate reminder times
- 📅 **Smart Date/Time Assignment**: Uses context to determine optimal timing
- 🏷️ **Category Classification**: Automatically categorizes tasks appropriately
- ⏰ **IST Timezone**: All operations use Indian Standard Time
- 🔄 **Multi-AI Fallback**: Uses Groq → Gemini → Cohere for reliability

## Request Format

### Headers
```
Content-Type: application/json
```

### URL Parameters
- `user_id` (string): User UUID identifier

### Request Body
```json
{
    "prompt": "string (required) - Natural language description of tasks to schedule"
}
```

## Example Requests

### Medical Appointments
```json
{
    "prompt": "I need to schedule a doctor appointment for next week and a dentist cleaning"
}
```

### Work Schedule
```json
{
    "prompt": "Schedule team meeting tomorrow at 10am, important client presentation on Friday"
}
```

### Fitness Planning
```json
{
    "prompt": "Plan my gym sessions for this week - cardio on Monday, strength training Wednesday"
}
```

### Mixed Activities
```json
{
    "prompt": "Schedule grocery shopping tomorrow, dinner with friends on Saturday, study session Sunday"
}
```

## Success Response (200 OK)

```json
{
    "success": true,
    "tasks": [
        {
            "title": "Doctor Appointment",
            "description": "Annual health checkup with Dr. Smith including blood work review and discussion of health concerns",
            "date": "2025-10-07",
            "time": "10:00",
            "category": "health",
            "reminder_setting": "2 hours"
        },
        {
            "title": "Dentist Cleaning",
            "description": "Regular dental cleaning and checkup to maintain oral health",
            "date": "2025-10-10",
            "time": "15:00", 
            "category": "health",
            "reminder_setting": "2 hours"
        }
    ]
}
```

## AI Reminder Intelligence Rules

### 🚨 Critical/Important Events → **"1 day" or "4 hours"**
- Job interviews, flights, surgery, weddings, important deadlines
- **Why**: Maximum advance notice for critical events

### 🏥 Medical/Health Appointments → **"2 hours"**
- Doctor visits, dentist, hospital, clinic appointments
- **Why**: Time needed for preparation, travel, and potential delays

### 💼 Work Meetings/Tasks → **"1 hour" or "2 hours"**
- Team meetings, client calls, presentations, conferences
- Important work tasks get 2 hours, regular meetings get 1 hour
- **Why**: Standard business preparation time

### ✈️ Travel Related → **"4 hours"**
- Flights, train bookings, trip preparations
- **Why**: Critical timing, traffic, check-in requirements

### 🏋️ Fitness/Gym → **"30 minutes"**
- Workouts, gym sessions, yoga, sports activities
- **Why**: Time to change clothes and mentally prepare

### 📚 Education/Learning → **"30 minutes"**
- Classes, courses, study sessions, training
- **Why**: Time to gather materials and prepare mentally

### 👥 Social Events → **"1 hour"**
- Parties, dinners, social gatherings, dates
- **Why**: Adequate preparation and travel time

### 🛍️ Shopping/Errands → **"1 hour"**
- Grocery shopping, market visits, errands
- **Why**: Plan route, make lists, check for deals

### 🔧 Maintenance/Repairs → **"2 hours"**
- Home repairs, vehicle service, equipment maintenance
- **Why**: Arrange time off work, gather tools/materials

### 💰 Finance/Banking → **"1 hour"**
- Bank appointments, tax meetings, financial planning
- **Why**: Gather necessary documents and information

### 📱 Personal Tasks → **"15 minutes"**
- General personal activities, routine tasks
- **Why**: Quick reminder for everyday activities

## Error Responses

### 400 Bad Request - Missing Prompt
```json
{
    "message": "Prompt is required"
}
```

### 500 Internal Server Error - AI Service Failure
```json
{
    "success": false,
    "message": "All AI services unavailable"
}
```

### 500 Internal Server Error - Processing Error
```json
{
    "success": false,
    "message": "Error generating tasks: [specific error]"
}
```

## AI Enhancement Process

1. **Natural Language Analysis**: AI understands the user's scheduling intent
2. **Task Extraction**: Identifies individual tasks within the prompt
3. **Context Analysis**: Determines task importance, type, and urgency
4. **Smart Scheduling**: Assigns appropriate dates and times
5. **Category Classification**: Automatically categorizes each task
6. **Intelligent Reminders**: Applies context-aware reminder settings
7. **Quality Assurance**: Ensures all required fields are present with fallbacks

## Example Workflows

### Scenario 1: Professional Schedule
**Input**: "Schedule important client meeting tomorrow, team standup Wednesday, project deadline Friday"

**AI Processing**:
- Client meeting → Work category → 2 hours reminder (important)
- Team standup → Work category → 1 hour reminder (regular)
- Project deadline → Work category → 1 day reminder (critical)

### Scenario 2: Health & Fitness
**Input**: "Doctor appointment next Monday, gym sessions Tuesday and Thursday"

**AI Processing**:
- Doctor appointment → Health category → 2 hours reminder
- Gym sessions → Fitness category → 30 minutes reminder each

### Scenario 3: Mixed Personal Tasks
**Input**: "Grocery shopping tomorrow, dinner with family Sunday, study for exam Monday"

**AI Processing**:
- Grocery shopping → Shopping category → 1 hour reminder
- Family dinner → Social category → 1 hour reminder
- Study session → Education category → 30 minutes reminder

## Technical Notes

- **Timezone**: All times are in Indian Standard Time (IST)
- **Date Format**: YYYY-MM-DD
- **Time Format**: HH:MM (24-hour)
- **Fallback System**: If AI fails, intelligent defaults are applied
- **Quality Control**: All generated tasks are validated and enhanced

## Integration with Add Task
Generated tasks can be individually added to the schedule using the `/api/{user_id}/ai/add-task` endpoint for further AI enhancement and database storage.

This endpoint provides a powerful way to quickly create comprehensive schedules from natural language, with intelligent automation handling the complex details of reminder timing.