# UI Automation

Android UI automation prototype using Python, ADB, and uiautomator2.

## Current capabilities

- Connect to an Android device through ADB
- Open Instagram
- Search for and verify a target profile
- Inspect grid posts
- Detect the Like or Liked state
- Process multiple posts
- Scroll through a profile
- Skip posts that are already Liked
- Target a configured number of new Likes
- Perform Instagram actions without fixed hardcoded screen coordinates

## Development tools

- [WEditor](https://github.com/alibaba/web-editor) can help inspect Android UI elements.
- [scrcpy](https://github.com/Genymobile/scrcpy) can mirror and control the device.
- `inspect_ui.py` dumps the current UI hierarchy to `hierarchy.xml` and can filter nodes for debugging. The generated XML file is ignored by Git because it may contain device or account data.
- `device_test.py` is a minimal device connection diagnostic.

## Setup

1. Create and activate a Python virtual environment.
2. Install the Python dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Install and configure ADB separately, then confirm that ADB already detects the Android device.
4. Optionally install WEditor and scrcpy for UI inspection and device mirroring.

## Configuration

Set the safe placeholder values near the top of `instagram_workflow.py` before running it:

```python
SERIAL = ""          # ADB serial or IP:PORT
TARGET_USERNAME = "" # Instagram username
TARGET_COUNT = 1      # Number of new Likes
```

`SERIAL` may be either a USB ADB serial or a wireless ADB `IP:PORT` endpoint. The debugging utilities have their own blank serial placeholders.

Run automation only against a device and account you are authorized to use. Local connection and account values should remain uncommitted.
