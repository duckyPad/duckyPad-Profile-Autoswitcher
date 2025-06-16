# duckyPad Autoswitcher macOS Notes

[Get duckyPad](https://duckypad.com) | [Official Discord](https://discord.gg/4sJCBx5)

---------

On macOS, you can run the autoswitcher as a **pre-packaged app**, or execute the **source code** directly.

## Pre-packaged App

* [Download the latest macOS release here](https://github.com/dekuNukem/duckyPad-profile-autoswitcher/releases/latest)

* Double click to unzip

* **Right Click** on the folder, select `New Terminal at Folder`

![Alt text](./resources/term.png)

* Type `sh ./run.sh`, press enter.

![Alt text](./resources/run.png)

* Authenticate, then the app should launch!

---------

* If macOS complaints about unsigned app

* Go to Settings > Privacy & Security

* Scroll down to security section and click "Allow Anyway" 

![Alt text](./resources/unknown.png)

![Alt text](./resources/perf.png)

## Run from Source

* [Download the latest source release here](https://github.com/dekuNukem/duckyPad-profile-autoswitcher/releases/latest)
* Double click to unzip
* **Right Click** on the folder, select `New Terminal at Folder`

----

* Use [homebrew](https://brew.sh) to install python-tk: `brew install python-tk`
* **[Optional]** Make a virtualenv and activate it: `python3 -m venv .venv; source .venv/bin/activate`
* Install dependencies: `pip3 install -r requirements.txt`
* Launch the Application: `sudo python3 ./duckypad_autoprofile.py`
