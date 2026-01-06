"""
Wayland-specific window detection for KDE Plasma.
This module provides functions to get active window information on KDE Plasma Wayland.
"""

import os
import subprocess
import psutil


def detect_wayland_compositor():
    """
    Detect if KDE Plasma (KWin) compositor is running.
    Returns: 'kwin' for KDE Plasma, or None if not detected.
    """
    # Check environment variables
    desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
    xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    # Check for KDE Plasma
    if desktop_session == 'plasma' or 'plasma' in desktop_session or 'kde' in xdg_current_desktop:
        return 'kwin'
    
    # Check if kwin is running
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] in ['kwin_wayland', 'kwin_wayland_wrapper']:
                return 'kwin'
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return None


def kwin_get_active_window():
    """
    Get active window information from KDE Plasma KWin using kdotool.
    Returns: tuple (app_name, window_title)
    
    Requires kdotool to be installed.
    Install on Arch Linux: yay -S kdotool-bin
    """
    try:
        # Check if kdotool is available
        try:
            subprocess.run(['kdotool', '--version'], 
                         capture_output=True, 
                         timeout=1, 
                         check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Warning: kdotool not found. Please install it for KDE Wayland support.")
            print("Install on Arch Linux: yay -S kdotool-bin")
            return '', ''
        
        # Get active window ID
        result = subprocess.run(['kdotool', 'getactivewindow'],
                              capture_output=True,
                              text=True,
                              timeout=1)
        
        if result.returncode != 0:
            return '', ''
        
        active_window = result.stdout.strip()
        if not active_window:
            return '', ''
        
        # Get window PID
        try:
            pid_result = subprocess.run(['kdotool', 'getwindowpid', active_window],
                                      capture_output=True,
                                      text=True,
                                      timeout=1)
            win_pid = int(pid_result.stdout.strip())
        except (ValueError, subprocess.SubprocessError):
            win_pid = None
        
        # Get process name from PID
        app_name = ''
        if win_pid:
            try:
                process = psutil.Process(win_pid)
                app_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                app_name = 'Unknown'
        else:
            app_name = 'Unknown'
        
        # Get window title
        try:
            wm_name_result = subprocess.run(['kdotool', 'getwindowname', active_window],
                                          capture_output=True,
                                          text=True,
                                          timeout=1)
            wm_name = wm_name_result.stdout.strip()
        except subprocess.SubprocessError:
            wm_name = ''
        
        if not wm_name:
            # Try to get class name as fallback
            try:
                class_result = subprocess.run(['kdotool', 'getwindowclassname', active_window],
                                            capture_output=True,
                                            text=True,
                                            timeout=1)
                wm_name = class_result.stdout.strip()
            except subprocess.SubprocessError:
                wm_name = 'Unknown'
        
        return (app_name, wm_name)
        
    except Exception as e:
        print(f"Error in KWin window detection: {e}")
        return '', ''


def kwin_get_list_of_all_windows():
    """
    Get list of all windows from KDE Plasma KWin using kdotool.
    Returns: list of tuples [(app_name, window_title), ...]
    
    Requires kdotool to be installed.
    """
    try:
        # Check if kdotool is available
        try:
            subprocess.run(['kdotool', '--version'], 
                         capture_output=True, 
                         timeout=1, 
                         check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            return []
        
        # Search for all windows - use '.*' argument for KDE 6 compatibility
        result = subprocess.run(['kdotool', 'search', '.*'],
                              capture_output=True,
                              text=True,
                              timeout=2)
        
        if result.returncode != 0:
            return []
        
        windows = []
        window_ids = list(filter(None, result.stdout.split('\n')))
        
        for window_id in window_ids:
            try:
                # Get window PID
                try:
                    pid_result = subprocess.run(['kdotool', 'getwindowpid', window_id],
                                              capture_output=True,
                                              text=True,
                                              timeout=1)
                    win_pid = int(pid_result.stdout.strip())
                except (ValueError, subprocess.SubprocessError):
                    win_pid = None
                
                # Get process name
                if win_pid:
                    try:
                        process = psutil.Process(win_pid)
                        app = process.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        app = 'Unknown'
                else:
                    app = 'Unknown'
                
                # Get window title
                try:
                    wm_name_result = subprocess.run(['kdotool', 'getwindowname', window_id],
                                                  capture_output=True,
                                                  text=True,
                                                  timeout=1)
                    wm_name = wm_name_result.stdout.strip()
                except subprocess.SubprocessError:
                    wm_name = 'Unknown'
                
                if not wm_name:
                    wm_name = 'Unknown'
                
                windows.append((app, wm_name))
                
            except Exception as e:
                print(f"Error processing window {window_id}: {e}")
                continue
        
        # Remove duplicates and sort
        windows = list(set(windows))
        windows.sort(key=lambda x: x[0])
        return windows
        
    except Exception as e:
        print(f"Error getting KWin windows list: {e}")
        return []


def wayland_get_active_window():
    """
    Get active window information on Wayland.
    Currently supports KDE Plasma (KWin) only.
    Returns: tuple (app_name, window_title)
    """
    compositor = detect_wayland_compositor()
    
    if compositor == 'kwin':
        return kwin_get_active_window()
    else:
        print("Warning: Unsupported Wayland compositor. Only KDE Plasma is currently supported.")
        return '', ''


def wayland_get_list_of_all_windows():
    """
    Get list of all windows on Wayland.
    Currently supports KDE Plasma (KWin) only.
    Returns: list of tuples [(app_name, window_title), ...]
    """
    compositor = detect_wayland_compositor()
    
    if compositor == 'kwin':
        return kwin_get_list_of_all_windows()
    else:
        print("Warning: Unsupported Wayland compositor. Only KDE Plasma is currently supported.")
        return []


if __name__ == "__main__":
    print("Detecting Wayland compositor...")
    compositor = detect_wayland_compositor()
    print(f"Detected compositor: {compositor}")
    
    print("\n----- Active Window -----")
    active = wayland_get_active_window()
    print(f"App: '{active[0]}'")
    print(f"Title: '{active[1]}'")
    
    if active[0] or active[1]:
        print("\n✅ SUCCESS! Active window detected!")
    else:
        print("\n❌ No active window detected")
    
    print("\n----- All Windows (first 10) -----")
    windows = wayland_get_list_of_all_windows()
    for app, title in windows[:10]:
        print(f"{app:30} | {title}")
