# 📂 TapTiles

**TapTiles** is a lightweight Windows app launcher written in **Python** using **Pygame**, designed to group and display applications in folders styled like an Android home screen.

> 🛠️ Originally started in Godot, this project was moved to pure Python due to engine limitations.

---

## ✨ Features

- **Drag & drop** apps directly into folders
- Compatible with `.exe`, `.lnk`, and `.url` files
- Works with Steam games
- Custom folders for different app categories
- Color customization for each folder
- Simple and portable

> ⚠️ Some apps like **PPSSPP** may hav issues, but it works with **95%+** of tested apps.

---

## 🚀 Getting Started

### 📦 Requirements

Install dependencies:
```bash
icoextract      # Para extraer íconos de ejecutables
Pillow (PIL)    # Para manejo de imágenes
pylnk3          # Para leer accesos directos .lnk
pygame          # GUI principal
pywin32         # Proporciona win32api, win32con, win32gui
```

### 📦 guide

# 🧠 How TapTiles Works

This section explains how the core script of **TapTiles** works, from reading arguments to rendering the interface and handling user interactions.

---

## 📥 1. **Imports and Dependencies**

The script imports standard modules (`os`, `sys`, `subprocess`, `json`, etc.) and third-party packages:

- `pygame`: Used for the GUI.
- `win32api`, `win32con`, `win32gui`: Used for window transparency.
- `get_icon`: Custom function to extract icons from `.exe` or `.lnk` files.
- `save_load_data`: Handles loading and saving app data (`data.json`).

---

## ⚙️ 2. **Command-line Arguments**

The script supports arguments for folder configuration:

- `--CodeName FolderName` → Loads or creates a folder named *FolderName*.
- `--BgCol r,g,b` → Sets background color.
- `--BorderCol r,g,b` → Sets border color.
- `--NoText` → Hides the folder title text (not yet implemented).

These arguments allow multiple folders with different sets of apps and visual styles.

---

## 🗂️ 3. **Folder and Data Setup**

- Creates a directory called `icon_cache` to store icon images.
- Initializes folder name, colors, and display options.
- Loads the list of app paths from `data.json` for the selected folder using `load_apps_from_folder`.

---

## 🪟 4. **Pygame Window Setup**

- Initializes a **600x600** borderless window (`pygame.NOFRAME`).
- Applies a **transparency color key** using the Windows API to simulate a rounded floating window.
- Draws a rounded rectangle background using the provided colors.

---

## 🎨 5. **Icon Layout and Loading**

### `get_apps()` function:

- Resolves `.lnk` files to `.exe` using `get_exe_from_lnk`.
- Extracts app icons via `get_icon()` and saves them to `icon_cache`.
- Loads and resizes icons into `64x64` sprites.
- Creates layout positions (`pygame.Rect`) for each icon in a grid.

---

## 🖱️ 6. **Main Loop**

The app enters a `while` loop that:

### 🔁 Continuously:

- Draws the background and border.
- Displays the folder title (if not disabled).
- Draws app icons, and if hovered, displays animated border highlighting.

### 🖱️ Handles Events:

- **QUIT** → Closes the app.
- **DROPFILE** → Accepts `.exe`, `.lnk`, or `.url` files and adds them to the current folder.
- **MOUSEBUTTONDOWN** → Detects clicks on icons and launches the selected app via `os.startfile`.

When a new app is added, it’s saved immediately to `data.json` using `save_folder_data`.

---

## 🧩 7. **Helper Functions**

### `lerp_color(color1, color2, t)`

Interpolates between two RGB colors to create smooth hover effects.

---

## 💾 8. **Data Format**

Stored in a `data.json` file like this:

```json
{
  "Games": {
    "apps": [
      "C:/Games/Steam.exe",
      "C:/Emulators/Dolphin/dolphin.exe"
    ]
  },
  "Work": {
    "apps": [
      "C:/Tools/Notepad++.exe"
    ]
  }
}
```

### 💾 How Folder Data Is Saved and Loaded

This module is responsible for managing the saving and loading of app lists per folder in a JSON file. It ensures that each folder ("CodeName") stores its own independent list of apps.

---

## 📁 File: `save_load_data.py`

### 🔧 `save_folder_data(file_path, folder_name, apps)`

**Purpose**:  
Saves (or updates) the list of applications associated with a specific folder name to a JSON file.

#### 🔍 Parameters:
- `file_path`: Path to the JSON file (e.g., `"data.json"`).
- `folder_name`: Name of the folder (like `"Games"` or `"Work"`).
- `apps`: A list of strings with app paths.

#### 💡 What it does:
1. Tries to load the existing JSON file if it exists.
2. Updates only the entry related to `folder_name`.
3. Writes the updated structure back to the file, nicely formatted.

#### 🧠 Example:
```python
save_folder_data("data.json", "Games", [
    "C:/Games/Steam.exe",
    "C:/Emulators/Dolphin.exe"
])
```

### 🖼️ Icon Extraction Logic (`get_icon.py`)

This module handles icon extraction from executable files (`.exe`), Windows shortcuts (`.lnk`), and internet shortcuts (`.url`). The extracted icons are converted into `.png` format and cached locally for display inside the TapTiles GUI.

---

## 🔧 `get_icon(exe_path, png_path)`

**Purpose**:  
Extracts the icon from an `.exe`, `.lnk`, `.url`, or `.ico` file and saves it as a `.png` in a specified directory.

### 🔍 Parameters:
- `exe_path`: Path to the target file (`.exe`, `.lnk`, `.url`, or `.ico`).
- `png_path`: Directory where the `.png` icon will be saved.

### 💡 Behavior:
1. If the path is a `.lnk` file:
   - Resolves it to the real `.exe` using `get_exe_from_lnk`.
2. If it's a `.url` file:
   - Extracts the icon path using `get_exe_from_url`.
3. If it's already an `.ico`:
   - Converts it directly to `.png`.
4. Otherwise:
   - Extracts the first embedded icon from the `.exe` using [`icoextract`](https://pypi.org/project/icoextract/).

### 🧠 Example:
```python
icon_path = get_icon("C:/Games/Steam.exe", "icon_cache")
