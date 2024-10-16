from datetime import datetime

def get_prompt(): return f'''
Current date: {datetime.now().strftime("%Y-%m-%d (%A)")}
Current time: {datetime.now().strftime("%H:%M")}
'''
