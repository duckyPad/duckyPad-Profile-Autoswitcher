"""
Wayland-specific window detection for various compositors.
This module provides functions to get active window information on Wayland.

Supported compositors:
- KDE Plasma (KWin) - requires kdotool
- Niri - uses built-in IPC (niri msg)
"""

import os
import subprocess
import json
import psutil


def detect_wayland_compositor():
    """
    Detect which Wayland compositor is running.
    Returns: 'kwin' for KDE Plasma, 'niri' for Niri, or None if not detected.
    """
    # Check environment variables
    desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
    xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    # Check for KDE Plasma
    if desktop_session == 'plasma' or 'plasma' in desktop_session or 'kde' in xdg_current_desktop:
        return 'kwin'
    
    # Check for Niri
    if 'niri' in xdg_current_desktop or desktop_session == 'niri':
        return 'niri'
    
    # Check running processes
    for proc in psutil.process_iter(['name']):
        try:
            proc_name = proc.info['name']
            if proc_name in ['kwin_wayland', 'kwin_wayland_wrapper']:
                return 'kwin'
            if proc_name == 'niri':
                return 'niri'
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


def niri_get_active_window():
    """
    Get active window information from Niri using niri msg IPC.
    Returns: tuple (app_name, window_title)
    
    Uses built-in niri IPC, no external dependencies required.
    """
    try:
        # Get focused window info as JSON
        result = subprocess.run(['niri', 'msg', '--json', 'focused-window'],
                              capture_output=True,
                              text=True,
                              timeout=1)
        
        if result.returncode != 0:
            return '', ''
        
        output = result.stdout.strip()
        if not output or output == 'null':
            return '', ''
        
        window_info = json.loads(output)
        
        # Extract app_id and title
        app_id = window_info.get('app_id', '') or ''
        title = window_info.get('title', '') or ''
        
        return (app_id, title)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing Niri JSON: {e}")
        return '', ''
    except FileNotFoundError:
        print("Warning: niri command not found.")
        return '', ''
    except Exception as e:
        print(f"Error in Niri window detection: {e}")
        return '', ''


def niri_get_list_of_all_windows():
    """
    Get list of all windows from Niri using niri msg IPC.
    Returns: list of tuples [(app_name, window_title), ...]
    
    Uses built-in niri IPC, no external dependencies required.
    """
    try:
        # Get all windows as JSON
        result = subprocess.run(['niri', 'msg', '--json', 'windows'],
                              capture_output=True,
                              text=True,
                              timeout=2)
        
        if result.returncode != 0:
            return []
        
        output = result.stdout.strip()
        if not output or output == 'null':
            return []
        
        windows_list = json.loads(output)
        
        windows = []
        for window_info in windows_list:
            app_id = window_info.get('app_id', '') or 'Unknown'
            title = window_info.get('title', '') or 'Unknown'
            windows.append((app_id, title))
        
        # Remove duplicates and sort
        windows = list(set(windows))
        windows.sort(key=lambda x: x[0])
        return windows
        
    except json.JSONDecodeError as e:
        print(f"Error parsing Niri JSON: {e}")
        return []
    except FileNotFoundError:
        print("Warning: niri command not found.")
        return []
    except Exception as e:
        print(f"Error getting Niri windows list: {e}")
        return []


def wayland_get_active_window():
    """
    Get active window information on Wayland.
    Supports: KDE Plasma (KWin), Niri.
    Returns: tuple (app_name, window_title)
    """
    compositor = detect_wayland_compositor()
    
    if compositor == 'kwin':
        return kwin_get_active_window()
    elif compositor == 'niri':
        return niri_get_active_window()
    else:
        print("Warning: Unsupported Wayland compositor. Supported: KDE Plasma, Niri.")
        return '', ''


def wayland_get_list_of_all_windows():
    """
    Get list of all windows on Wayland.
    Supports: KDE Plasma (KWin), Niri.
    Returns: list of tuples [(app_name, window_title), ...]
    """
    compositor = detect_wayland_compositor()
    
    if compositor == 'kwin':
        return kwin_get_list_of_all_windows()
    elif compositor == 'niri':
        return niri_get_list_of_all_windows()
    else:
        print("Warning: Unsupported Wayland compositor. Supported: KDE Plasma, Niri.")
        return []


if __name__ == "__main__":
    print("Detecting Wayland compositor...")
    compositor = detect_wayland_compositor()
    print(f"Detected compositor: {compositor}")
    
    if compositor == 'kwin':
        print("  -> Using kdotool for KDE Plasma")
    elif compositor == 'niri':
        print("  -> Using niri msg IPC (no external dependencies)")
    else:
        print("  -> No supported compositor detected")
    
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
