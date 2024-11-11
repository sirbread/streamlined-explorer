# Streamlined Explorer

An optimized and fast Windows file explorer built using PyQt5, designed for smooth navigation, (kinda) advanced file operations, and efficient searches across directories. <br>
Currently Windows only.

## requirements!

- **Python 3.6+**
- **PyQt5 library**: Install with `pip install PyQt5`

## running it!

1. Clone thy repo.
2. Install the required libraries (see requirements).
3. Run the program with the command:
    ```bash
    python streamlined_explorer.py
    ```

## stuff it does!

- **Directory Navigation**: Efficient navigation through folders and files with a convenient backtracking function.
- **File Operations**:
  - **Rename**: Rename selected files or folders.
  - **Delete**: Delete selected files or folders with confirmation prompts.
  - **View Properties**: Display file/folder details, including size, type, and last modified date.
  - **New Folder/File Creation**: Add new folders or files directly within the application.
- **Keyboard Shortcuts**:
  - **Backspace**: Navigate to the parent directory.
  - **Enter**: Open selected file or folder.

## ui overview!

- **Path Bar**: Displays the current directory path. Allows typing to navigate to a specific path.
- **File Table**: Displays files and folders in the current directory with details on name, date modified, and size.
- **Buttons**:
  - **Open Folder**: Opens a directory.
  - **View Properties**: Shows details of the selected file/folder.
  - **Rename Selected Item**: Renames a selected file or folder.
  - **Delete Selected Item**: Deletes the selected item.
  - **New Folder/File**: Allows creation of a new file or folder.
  
## enjoy!
