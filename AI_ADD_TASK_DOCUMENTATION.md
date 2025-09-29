# AI ADD TASK Endpoint Documentation

## Endpoint
`POST /api/{user_id}/ai/add-task`

## Description
AI-powered task creation endpoint that intelligently processes and enhances task data before saving it to the database. This endpoint automatically calculates the reminder datetime based on the provided reminder setting and optionally uses AI to enhance the task description and validate the category. **All times are handled in Indian Standard Time (IST) by default.**

## Features
- ✨ **AI Enhancement**: Improves task descriptions and validates categories using AI
- ⏰ **Auto Reminder Calculation**: Automatically calculates `reminder_datetime` based on task datetime and reminder setting
- 🇮🇳 **IST Timezone**: All date/time operations use Indian Standard Time (IST) by default
- 🔄 **Multi-AI Fallback**: Uses Groq → Gemini → Cohere for reliability
- ✅ **Comprehensive Validation**: Validates all input fields and formats
- 📊 **Detailed Response**: Returns enhanced task data and creation status

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
    "title": "string (required)",
    "description": "string (required)",
    "category": "string (required)",
    "date": "YYYY-MM-DD (required, IST timezone assumed)",
    "time": "HH:MM (required, 24-hour format, IST timezone assumed)",
    "done": "boolean (optional, default: false)",
    "reminder_setting": "string (required, format: 'X unit')"
}
```

### Reminder Setting Format
- `"15 minutes"` - 15 minutes before task
- `"1 hour"` - 1 hour before task  
- `"2 hours"` - 2 hours before task
- `"1 day"` - 1 day before task
- `"2 days"` - 2 days before task
- `"1 week"` - 1 week before task

## Example Request
```bash
curl -X POST "http://127.0.0.1:5000/api/8620b861-ea55-478a-b1b4-f266cb6a999d/ai/add-task" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Gym Session",
    "description": "Scheduled gym session at the gym",
    "category": "fitness",
    "date": "2025-09-30",
    "time": "07:00",
    "done": false,
    "reminder_setting": "15 minutes"
  }'
```

## Success Response (201 Created)
```json
{
    "success": true,
    "message": "AI task added successfully!",
    "task_id": 123,
    "task_data": {
        "user_id": "8620b861-ea55-478a-b1b4-f266cb6a999d",
        "title": "Gym Session",
        "description": "Complete 45-minute gym workout focusing on cardio and strength training at the local gym facility",
        "category": "fitness",
        "date": "2025-09-30",
        "time": "07:00",
        "done": false,
        "reminder_setting": "15 minutes",
        "reminder_datetime": "2025-09-30 06:45:00"
    },
    "ai_enhanced": true
}
```

## Error Responses

### 400 Bad Request - Missing Fields
```json
{
    "error": "Missing required field: title"
}
```

### 400 Bad Request - Invalid Date/Time Format
```json
{
    "error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time (IST)"
}
```

### 400 Bad Request - Invalid Reminder Setting
```json
{
    "error": "Invalid reminder_setting format. Use format like '15 minutes', '1 hour', '2 days'"
}
```

### 500 Database Error
```json
{
    "error": "Database error: [specific error message]"
}
```

### 500 Server Error
```json
{
    "error": "An unexpected error occurred: [specific error message]"
}
```

## AI Enhancement Details

### Description Enhancement
The AI will improve task descriptions to be more:
- Detailed and actionable
- Concise but informative
- Professionally formatted

### Category Validation
Common validated categories:
- `work` - Professional tasks
- `personal` - Personal activities
- `health` - Health-related tasks
- `fitness` - Exercise and physical activities
- `education` - Learning and study tasks
- `shopping` - Purchase-related tasks
- `social` - Social events and meetings
- `travel` - Travel-related tasks
- `maintenance` - Home/vehicle maintenance
- `finance` - Financial tasks

## Database Schema
The task is saved to the `events` table with these fields:
- `user_id` - User identifier
- `title` - Task title
- `description` - Enhanced task description
- `category` - Validated category
- `date` - Task date (YYYY-MM-DD format)
- `time` - Task time (HH:MM format in IST)
- `done` - Completion status
- `reminder_setting` - Original reminder setting
- `reminder_datetime` - Calculated reminder datetime (in IST)
- `reminde1`, `reminde2`, `reminde3`, `reminde4` - Reminder flags (all set to false)

## Dependencies
- Flask
- mysql-connector-python
- python-dotenv
- datetime
- json
- AI APIs: Google Gemini, Groq, Cohere (optional but recommended)

## Environment Variables Required
```
GOOGLE_GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key  
COHERE_API_KEY=your_cohere_key
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_DATABASE=your_database_name
```

## Testing
Use the included `test_ai_add_task.py` script:
```bash
python test_ai_add_task.py
```

## Integration Notes
- This endpoint is part of the `ai_scheduler_bp` Blueprint
- It integrates with the existing database schema
- Works alongside other task management endpoints
- Provides AI-enhanced functionality while maintaining backward compatibility