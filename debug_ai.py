from ai_scheduler import AIScheduler

try:
    scheduler = AIScheduler()
    result = scheduler.generate_tasks("Create a task for tomorrow at 2pm to call the dentist")
    print("Success!")
    print("Result:", result)
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()