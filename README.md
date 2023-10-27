# MIE444-2023-Team-11
Team 11 repository for MIE444 project, 2023.

## Team Members
- Emma Day
- Nate Lansil
- Jeff Guo
- Ferdinand Tonby-Strandborg

# To Do
## Milestone 1
- **Motor**
- [ ] Get arduino to control 4 motors
- [ ] Setup "emergency stop" logic
- [ ] Enable "progress" to be returned
- [ ] Attach to wheels, robot
- [ ] Callibrate motion
- **Sensor**
- [ ] Get arduino to control Ultrasonic Sensors
- [ ] Calibrate US sensors for distance
- [ ] Get arduino to control Gyroscope
- [ ] Calibrate Gyro for accel
- [ ] Attach to robot
- [ ] Declare "emergency stop" logic
- [ ] Define "direction block" logic
- **Robot Bluetooth**
- [ ] Setup ESP32 to communicate over bluetooth
- [ ] Setup pass-along logic to pass messagea to Arduinos
- **Bluetooth Node**
- [ ] Setup bluetooth "node", exposing data in socket on comouter
- [ ] Setup "master" logic for where to accept control inputs (from control software, or from manual input)
- **Control Software**
- [ ] Setup control logic
- **Visualization**
- [ ] Setup visual for motor relative to current ultrasonic walls
- [ ] Setup wheel speed motion representation
- [ ] Setup input detection (W, A, S, D, Q, E)
- [ ] Setup wall "history" view

# Using Git
<br>**[Aside] Breifly, what is Git?**
<br>Git is a version control tool that shows changes to the files contained inside *repositories*.
<br>When using Git you will (almost always) have:
- A **remote repository**. This is what your are looking at now on GitHub.com. You can think of this as the "official" version(s) of the repository.
- A **local repository**. This is what you will be working on on your local computer. You can think of this as your "personal" version, or "temporary" version(s).
In order to create your **local repository**, you should use a Git **clone**. I recommend using **GitHub Desktop** to do this, as it makes it easier.
<br>In order to update your **local repository** to match the **remote repository**, you should use a Git **pull**. This will update changes to the **remote repository** on you local computer, but it **WILL NOT** overwrite your local changes.
<br>In order to "store" or "save" your changes locally, you use a Git **commit**. This **WILL NOT** update the **remote repository**. It is good practice to apply appropriate messages to keep track and overview over changes.
<br> In order to update the **remote repository**, you use a Git **push**. This will send all the **commit**s from your local computer to the **remote repository**.

## GitHub Desktop
I recommend downloading the github Desktop App, this will make it easier to get started with Git and GitHub. You can download it from [GitHub Desktop](https://desktop.github.com/). Ensure that it is downloaded, and set up with your GitHub account before proceeding.

### Cloning
In order to clone this repository, ...
<br>For this repository, the URL is "[https://github.com/Ferdi0412/MIE444-2023-Team-11.git](https://github.com/Ferdi0412/MIE444-2023-Team-11.git)".
1. In the GitHub Desktop app, press down ***File*** on the header bar, and press "Clone repository...".
2. In the popup that appears, titled "Clone a repository", go to the "URL" tab.
3. Insert the repository URL under the "Repository URL or GitHub username and repository (hubot/cool-repo)"
4. Apply where in your computer to store the **local repository** under "Local path"
<br>![Clone In GitHub Desktop](https://github.com/Ferdi0412/MIE444-2023-Team-11/assets/78992348/c509e854-3ec8-448b-b56f-dd05e7e26f1a)
*Clone repo popup in GitHub Desktop*
<br>![After Clone GitHub Desktop](https://github.com/Ferdi0412/MIE444-2023-Team-11/assets/78992348/66ebc845-5025-4fac-ae66-6500565e3ee8)
*After cloning in GitHub Desktop*

### Pull
In order to keep you **local repository** up-to-date, you should regularly pull from the **remote repository**. To do so, use **Repository > Pull** in the header of the GitHub Desktop, or pressing "ctrl + shift + p" in the same app.

### Changes and Commits
As you update files in your **local repository**, you will see changes appear in the GitHub Desktop app (assuming the "Current repository" in the top left corner shows the correct repo).
<br>![GitHub Desktop After Changes](https://github.com/Ferdi0412/MIE444-2023-Team-11/assets/78992348/41ad804b-6031-41f9-9e42-6bfddf5b79a3)
*Image showing a new image was added*
<br>Notice that the image is a new file in the repository, and therefore it is outlined by <span style="color:green">**green**</span> lines. Green indicates new files and lines, red means files/lines were removed, and orange indicates changes to the same.
<br>You can see changes to text-readable files by individual lines.
<br>In order to **commit** the changes, you can use the bottom left field of the GitHub Desktop app. Note that a message ("Summary") is required.
<br>![GitHub Desktop After Changes Text](https://github.com/Ferdi0412/MIE444-2023-Team-11/assets/78992348/996f7b1a-0cf4-4e52-a109-24f751767161)
*Image showing commit message fields*
<br>![GitHub Desktop Commit Message](https://github.com/Ferdi0412/MIE444-2023-Team-11/assets/78992348/489012b0-45c6-431b-b5be-b4df3c329758)
*Image showing example commit message*
<br>Once one or more commits have been made, you can do a Git **push**.

### Push
[NOTE] In order to ensure no **conflicts** occur (this happens when someone else **commit**s and **push**es a change to the **remote repository** after your last **pull**, so your **local repository** and the **remote repository** do not have the same history (this is called "branching").
<br>To **push**, press **Repository > Push** in the GitHub Desktop.
<br>![GitHub Desktop Post Commit](https://github.com/Ferdi0412/MIE444-2023-Team-11/assets/78992348/61c72c6c-7e32-48af-9a6a-755ec3b0c0f7)
*Image showing Rpository tab in header*.

# Simmer
The simmer-python-main sub-directory is derived from the [simmer](https://github.com/ian612/simmer-python) repository by [Ian Bennett](https://github.com/ian612).
