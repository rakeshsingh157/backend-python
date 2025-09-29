# How to Send API Request with Postman - AI ADD TASK Endpoint

## Step-by-Step Guide

### 1. Open Postman
- Download and install Postman from https://www.postman.com/downloads/
- Open Postman application

### 2. Create New Request
- Click "New" or "+" tab
- Select "HTTP Request"

### 3. Configure the Request

#### Method
- Change from GET to **POST**

#### URL
```
http://127.0.0.1:5000/api/8620b861-ea55-478a-b1b4-f266cb6a999d/ai/add-task
```
*Replace `8620b861-ea55-478a-b1b4-f266cb6a999d` with your actual user_id*

#### Headers
1. Click on "Headers" tab
2. Add the following header:
   - **Key**: `Content-Type`
   - **Value**: `application/json`

#### Body
1. Click on "Body" tab
2. Select "raw" radio button
3. Select "JSON" from the dropdown (right side)
4. Paste the following JSON:

```json
{
    "title": "Gym Session",
    "description": "Scheduled gym session at the gym",
    "category": "fitness",
    "date": "2025-09-30",
    "time": "07:00",
    "done": false,
    "reminder_setting": "15 minutes"
}
```

### 4. Send the Request
- Click the blue "Send" button
- Wait for the response

## Expected Response (Success - 201 Created)

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

## Sample Test Cases

### Test Case 1: Basic Task
```json
{
    "title": "Doctor Appointment",
    "description": "Annual checkup with Dr. Smith",
    "category": "health",
    "date": "2025-10-01",
    "time": "14:30",
    "reminder_setting": "1 hour"
}
```

### Test Case 2: Work Meeting
```json
{
    "title": "Team Meeting",
    "description": "Weekly team standup meeting",
    "category": "work",
    "date": "2025-10-02",
    "time": "09:00",
    "reminder_setting": "30 minutes"
}
```

### Test Case 3: Personal Task
```json
{
    "title": "Grocery Shopping",
    "description": "Buy vegetables and fruits for the week",
    "category": "personal",
    "date": "2025-10-03",
    "time": "18:00",
    "reminder_setting": "2 hours"
}
```

## Error Testing

### Test Invalid Date Format
```json
{
    "title": "Test Task",
    "description": "Test Description",
    "category": "test",
    "date": "30-09-2025",
    "time": "07:00",
    "reminder_setting": "15 minutes"
}
```
**Expected**: 400 Bad Request - Invalid date format

### Test Missing Required Field
```json
{
    "description": "Test Description",
    "category": "test",
    "date": "2025-09-30",
    "time": "07:00",
    "reminder_setting": "15 minutes"
}
```
**Expected**: 400 Bad Request - Missing required field: title

## Postman Collection Setup

### Save Request
1. Click "Save" button (top right)
2. Create a new collection called "AI Task Manager API"
3. Save the request as "AI Add Task"

### Environment Variables (Optional)
1. Click on "Environments" in left sidebar
2. Create new environment "Local Development"
3. Add variables:
   - `base_url`: `http://127.0.0.1:5000`
   - `user_id`: `8620b861-ea55-478a-b1b4-f266cb6a999d`

4. Update request URL to:
```
{{base_url}}/api/{{user_id}}/ai/add-task
```

## Troubleshooting

### Common Issues

1. **Connection Refused Error**
   - Make sure Flask server is running: `python app.py`
   - Check if server is listening on port 5000

2. **404 Not Found**
   - Verify the URL is correct
   - Ensure the Flask server restarted after code changes

3. **500 Internal Server Error**
   - Check Flask server console for error messages
   - Verify database connection is working

4. **400 Bad Request**
   - Check JSON syntax is valid
   - Ensure all required fields are present
   - Verify date/time format is correct (YYYY-MM-DD and HH:MM)

### Server Status Check
First test if server is running:
- Method: **GET**
- URL: `http://127.0.0.1:5000/`
- Expected: HTML response (login page)

## Advanced Testing

### Testing AI Enhancement
The AI will enhance your task description and category. Compare the input vs output to see AI improvements.

### Testing Different Reminder Settings
Try these reminder_setting values:
- `"5 minutes"`
- `"30 minutes"`
- `"1 hour"`
- `"2 hours"`
- `"1 day"`
- `"1 week"`

### Testing Different Categories
Valid categories include:
- `"work"`
- `"personal"`
- `"health"`
- `"fitness"`
- `"education"`
- `"shopping"`
- `"social"`
- `"travel"`
- `"maintenance"`
- `"finance"`

## Export/Import Collection

### Export
1. Right-click on your collection
2. Choose "Export"
3. Select Collection v2.1
4. Save the JSON file

### Import
1. Click "Import" button
2. Upload the collection JSON file
3. All requests will be imported

This comprehensive guide should help you test the AI ADD TASK endpoint effectively with Postman!