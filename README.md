# FS2425_OTUI

## About this project

This project was created for the experimental setup of the paper ["Can't (Midas) touch this: An Evaluation of clutching methods for Opportunistic Tangible Interfaces on Interactive Tabletops"](https://todo.link/the/paper/once/it/is/published.org). It uses hand- and marker tracking (for the participant) and a Novation Launchpad (for the researcher) to facilitate system input. AprilTags are used to make everyday objects interactable.

Three interaction techniques are currently implemented: 2-D finger sliding, rotating, and page turning (implemented by checking for the visibility of different markers). 
Other functions can be triggered manually through the launchpad, to facilitate a Wizard-of-Oz-style simulation of other interaction techniques.

The project also includes scripts that control the procedure of the experiment for two tasks and two conditions per task.

## How it works

The setup requires a top-mounted projector and a calibrated RGB camera mounted above a desk. The camera tracks hands using [Google Mediapipe](https://research.google/blog/on-device-real-time-hand-tracking-with-mediapipe/) and objects using AprilTags. 

## Requirements

- Windows >=10
- Python >= 3.10

## Installation
 - `git clone "https://github.com/MaximilianKilger/Cant-Midas-Touch-this-Experimental-Setup.git"`
 - `cd Cant-Midas-Touch-this-Experimental-Setup`
 -  `pip install -r requirements.txt`
  
## Preparation
- Calibrate your camera. Replace `/util/Logitech BRIO 0 2K` with the calibration data or paste your calibration yml-file into `/util` and replace the value of `CALIBRATION_FILEPATH` in `/util/constants.py`.
- Print `/resources/apriltags_labeled.png`, cut out the markers and affix them to the top of their corresponding objects. (We used double-sided adhesive tape for this - it worked pretty well)
- Hang your camera and your projector above the table. Make sure that the field of view of the camera and the projection area of the projector closely correspond to the surface of the table, and that camera or projector don't occlude each other.
- Run `util/surface_selector.py` and select the four corners of the projector image. (This is easier if you mark the corners on the table first, either with tape or wipeable marker).
## Usage
 `cd src`
For task 1:
  `python -m task1.task1_manager [condition]`

For task 2:
  `python -m task2.task2_manager [condition]`

`condition` can be 0 or 1, selecting one of the two variations of each task. The different conditions vary in the text documents used in task 1 and the images used in task 2.

Tangibles can be *active* or *inactive*. Interaction is possible only in the *active* state. 
A Novation Launchpad is used to switch between the two states, as well as for triggering certain interactions in the tangibles' stead (mostly through keyboard shortcuts). 

The Launchpad's buttons are arranged in a 9x9 grid, from Button (0,0) in the top left to (8,8) in the bottom right. Each Tangible is assigned a column of buttons on the launchpad: The lowest button makes the tangible *active* or *inactive*; the second lowest button triggers its primary function, and the third lowest button can trigger a secondary function. For example, The scissors are assigned column 1 (second from the left), so pressing button (1,8) activates or deactivates the scissors, (1,7) triggers their primary shortcut `Ctrl+X`, and (1,6) triggers their secondary keyboard shortcut `Backspace`. Button (8,8) is assigned to activate / deactivate all tangibles at once. Button (0,1) is also assigned to switch all windows to fullscreen, for convenience.

|Tangible | AprilTag ID | Controlled with | Launchpad Column | Function (Task 1) | alternative Function (Task 1) | Function (Task 2) |
|---|---|---|---|---|---|---|
|highlighter|1|Launchpad |0| `Ctrl+A` | - | mark image with red circle |
|scissors|2| Launchpad |1| `Ctrl+X` |`Backspace` | - |
|gluestick|4| Launchpad |2| `Ctrl+V` | - | - |
|stapler|0|Launchpad|3| `Ctrl+Alt+M` | - | - |
|eraser|3|Launchpad|4|`Esc`|`Ctrl+Z`| - |
|bottle|9|Rotation|5|`Mouse Wheel`| - |Zoom|
|folder|8|Fingertip Position in Bounding Box|6| - | - | Move viewport|
|notepad| 5/6/7 | Revealing / Occluding Markers |7| Switching between Applications | - | Switching between pictures |

