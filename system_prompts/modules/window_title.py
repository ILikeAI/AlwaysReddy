import platform

def get_prompt():
    if platform.system() == "Darwin":  # macOS
        try:
            import AppKit
            app = AppKit.NSWorkspace.sharedWorkspace().activeApplication()
            return f'''
Current application: {app['NSApplicationName']}
'''
        except ImportError:
            return '''
Current window title not avaialable
'''
    elif platform.system() == "Windows":
        try:
            import pygetwindow as gw
            return f'''
Current window title: {gw.getActiveWindowTitle()}
'''
        except ImportError:
            return '''
Current window title not available
'''
    else:
        return '''
Current window title not available
'''
