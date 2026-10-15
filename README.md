# Envrionment

## Develop environment

Fedora linux. Kernel 7.2.9-200.fc44.x86_64

## Required python packages

- customtkinter
- openpyxl

# create a desktop launcher file

Due to working directory setup issue, I am now using a shell script wrapper. `shell_wrapper.sh`:

```bash
#!/usr/bin/bash
cd /path/to/workinghour_tracker_folder
/usr/bin/python3 main.py
```

create a desktop file in terminal with command: `nano ~/.local/share/applications/hour-tracker.desktop`. Then, paste the below content into the `hour-tracker.desktop` file:

```TOML
[Desktop Entry]
Type=Application
Name=Working Hour Tracker
Comment=Tracks daily working hours
Exec=setsid /path/to/workinghour_tracker_folder/shell_wrapper.sh >/dev/null 2>&1 &
Icon=/path/to/workinghour_tracker_folder/office-chair-svgrepo-com.svg
Terminal=false
Categories=Utility;
```

This script calls the shell wrapper in the desktop launcher file and prevent bringing up the terminal window. You can choose your own icon and place the icon name after `Icon=`. To customise it, find a svg image file and provide the path to the file. For example, download [this office chair icon from svg repo](https://www.svgrepo.com/svg/530656/office-chair) to the folder of the scripts. The image `office-chair-svgrepo-com.svg` can be directly sourced as in the above script.

As I am using the [Papirus Icons](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), I can browse through icon images in `/usr/share/icons/Papirus/48x48/apps/` in my file manager to find the one I like. For example, the snail icon `ch.x29a.playitslowly.svg` should be sourced as `Icon=ch.x29a.playitslowly` (without the extension).

Make the desktop file executable:

```bash
chmod +x ~/.local/share/applications/hour-tracker.desktop
```

now you have turned your python script into a desptop app!

If you went back to edit the desktop file, update the information to the system via `update-desktop-database ~/.local/share/applications` command in the terminal.

# Windows

Python can also be run on windows. How can I make it into a windows desktop app?

To implement the same behavior on Windows so other users can easily run your Python script as a desktop app with the correct working directory, you can use a Windows batch file (`.bat`) combined with a standard Windows desktop shortcut.

**1. Create a Batch Wrapper Script：** Save inside your project folder

Create a file named `run.bat` in your project folder. This file will ensure the command prompt switches to your project directory before launching Python:

```
@echo off
cd /d "%~dp0"
python main.py
pause
```

_(Note: `cd /d "%~dp0"` automatically sets the working directory to wherever this batch file lives, and `pause` keeps the window open so you can see any output or errors)._

_Verification:_ Double-click `run.bat` directly; it should open a command prompt, change to the project directory, and run your script successfully.

**2. Create a Desktop Shortcut：** Point to the batch file

Right-click anywhere on your Windows desktop, select **New** > **Shortcut**, and browse to select your `run.bat` file. Give it a descriptive name (e.g., "My Python App") and finish.

_Verification:_ Double-click the newly created desktop shortcut to ensure it launches the app correctly.

**3. Customize the Shortcut Icon (Optional)：** Make it look professional

Right-click your new desktop shortcut, select **Properties**, click the **Shortcut** tab, and click **Change Icon...** to choose an `.ico` file if you want a custom logo for your app. Note that windows uses ico files as icon instead of svg images. You can find free ico files online or use online tools to convert images to ico format.

_Verification:_ The desktop shortcut will now display your custom icon.

**4. Hide terminal window in Windows (Optional):** execute in background

Option 1) Create a `run.vbs` file in the project folder to source the `run.bat` file:

```VBScript
CreateObject("Wscript.Shell").Run chr(34) & "C:\path\to\your\workinghour-tracker\run.bat" & chr(34), 0, False
Set WshShell = Nothing
```

Option 2) Rewrite the `run.bat` into a `run.vbs` file:

```VBScript
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\path\to\your\workinghour-tracker"
WshShell.Run "python main.py", 0, False
Set WshShell = Nothing
```

Double click `run.vbs` to run the program.
