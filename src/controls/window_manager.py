import os
import time
import win32gui
import win32con

# Handles launching of and switching between different applications.
# Works only on Windows.
class WindowManager:

    # @param state_app_map: Dict with states(ints) as keys and paths to apps as values.
    def __init__(self, state_app_map):
        self.window_handlers = {}
        self.state_app_map = state_app_map
        self.active_state = None
        
    # receives an integer and a path to an application / file.
    # Launches that application or opens that file and tracks its window (using that integer).
    def start_application(self, state_id, app_path):
        if state_id in self.window_handlers and self.window_handlers[state_id]:
            print(f"Application for marker {state_id} is already running.")
            
            self.active_marker = state_id
            return

        if app_path:
            print(f"Starting application for marker {state_id}: {app_path}")
            os.system(f'start "" "{app_path}"')
            time.sleep(4)  # Allow time for the application to start
            self.window_handlers[state_id] = self.get_window_handler(app_path)
        else:
            print(f"No application mapped for marker {state_id}.")

    # maximizes a window specified by state_id
    def maximize(self, state_id):
        handler = self.window_handlers.get(state_id)
        
        self.active_marker = state_id
        if handler:
            print(f"Maximizing window for marker {state_id}.")
            try:
                win32gui.ShowWindow(handler, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(handler)
            except RuntimeError as e:
                print(e)
        else:
            print(f"No window handler found for marker {state_id}. Retrying.")
            self.window_handlers[state_id] = None  # Optionally, reset the handler
            time.sleep(0.25)

    #minimizes a window specified by state_id
    def minimize(self, state_id):
        handler = self.window_handlers.get(state_id)
        if handler:
            print(f"Minimizing window for marker {state_id}.")
            win32gui.ShowWindow(handler, win32con.SW_MINIMIZE)
            time.sleep(0.25)
        else:
            print(f"Cannot minimize: No handler found for marker {state_id}.")

    # gets a handler for a specific window
    def get_window_handler(self, app_path):
        def enum_windows_callback(handler, window_handles):
            title = win32gui.GetWindowText(handler).lower()
            class_name = win32gui.GetClassName(handler)
            if win32gui.IsWindowVisible(handler):
                if "editor" in title.lower() or "editor" in class_name.lower():
                    window_handles.append(handler)
                elif "firefox" in title.lower() or "firefox" in class_name.lower():
                    window_handles.append(handler)

        handles = []
        win32gui.EnumWindows(enum_windows_callback, handles)
        return handles[0] if handles else None

    # utility class to print all active windows
    def list_all_windows(self):
        def enum_windows_callback(handler, _):
            title = win32gui.GetWindowText(handler)
            class_name = win32gui.GetClassName(handler)
            print(f"Handler: {handler}, Title: '{title}', Class: '{class_name}', Visible: {win32gui.IsWindowVisible(handler)}")
        win32gui.EnumWindows(enum_windows_callback, None)

    # switches to a window specified by state_id
    def switch_to_window(self, state_id):
        
        if self.active_state != state_id:
            if self.active_state in self.window_handlers:
                self.minimize(self.active_state)
            
            app_path = self.state_app_map.get(state_id)
            if state_id in self.window_handlers:
                self.maximize(state_id)
            else:
                self.start_application(state_id, app_path)

            self.active_state = state_id
        

