# duckyPad Profile Auto-switcher

[Get duckyPad](https://duckypad.com) | [Official Discord](https://discord.gg/4sJCBx5)

This app allows your duckyPad to **switch profiles automatically** based on **current active window**.

![Alt text](resources/switch.gif)

## User Manual

### Windows

* 👉 [Download the latest release](https://github.com/dekuNukem/duckyPad-profile-autoswitcher/releases/latest)

Extract `.zip` file and launch the app by clicking `duckypad_autoprofile.exe`:

![Alt text](resources/app.png)

Windows might complain. Click `More info` and `Run anyway`.

Feel free to [review the files](./src), or run the source code directly with Python.

![Alt text](resources/defender.png)

### macOS / Linux

* 👉 [See instructions here!](https://dekunukem.github.io/duckyPad-Pro/doc/linux_macos_notes.html)

* **[LINUX ONLY]** Window detection not working? You might need to implement your own `get_list_of_all_windows()` and `get_active_window()` in `get_window.py`.

### Using the App

Your duckyPad should show up in the `Connection` section.

![Alt text](resources/empty.png)

Profile-Autoswitching is based on a list of *rules*.

To create a new rule, click `New rule...` button:

![Alt text](resources/rulebox.png)

A new window should pop up:

![Alt text](resources/new.png)

Each rule contains **Application name**, **Window Title**, and the **Profile** to switch to.

**`App name`** and **`Window Title`**:
* Type the keyword you want to match
* **NOT** case sensitive

**`Jump-to Profile`**:

* **Profile Name** to switch to when matched.
	* Full Name
	* **Case Sensitive**

Click `Save` when done.

Current active window and a list of all windows are provided for reference.

-------

Back to the main window, duckyPad should now automatically switch profile once a rule is matched!

![Alt text](resources/active_rules.png)

* Rules are evaluated **from top to bottom**, and **stops at first match**!

* Currently matched rule will turn green. 

* Select a rule and click `Move up` and `Move down` to rearrange priority.

* Click `On/Off` button to enable/disable a rule.

That's pretty much it! Just leave the app running and duckyPad will do its thing!

## System Tray Support

The app can minimize to the system tray instead of closing completely.

* When you close the main window, it will minimize to the system tray.

* Click the system tray icon to show the window again.

* Right-click the system tray icon and select "Quit" to exit the application completely.

### Start Minimized to System Tray

You can start the app minimized to the system tray using the `--minimized` command-line argument:

**Windows:**
```
duckypad_autoprofile.exe --minimized
```

**macOS / Linux:**
```
python3 duckypad_autoprofile.py --minimized
```

This is useful for auto-starting the app on system boot without showing the window.

## Launch Autoswitcher on Windows Startup

The easiest way is to place a shortcut in the Startup folder:

* Select the autoswitcher app and press `Ctrl+C`.

* Press `Win+R` to open the `Run...` dialog, enter `shell:startup` and click OK. This will open the Startup folder.

* Right click inside the window, and click "Paste Shortcut".

* (Optional) Edit the shortcut properties and add `--minimized` to the Target field after the executable path to start minimized to system tray. 

## HID Command Protocol

You can also write your own program to control duckyPad.

[Click me for details](HID_details.md)!

## Questions or Comments?

Please feel free to [open an issue](https://github.com/dekuNukem/duckypad/issues), ask in the [official duckyPad discord](https://discord.gg/4sJCBx5), DM me on discord `dekuNukem#6998`, or email `dekuNukem`@`gmail`.`com` for inquires.

