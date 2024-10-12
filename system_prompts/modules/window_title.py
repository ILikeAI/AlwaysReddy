import pygetwindow as gw

def get_prompt(): return f'''
Current window title: {gw.getActiveWindowTitle()}
'''
