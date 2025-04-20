import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QFileSystemModel, QTreeView, QMessageBox)
from PyQt5.QtCore import Qt, QDir, pyqtSignal, QModelIndex, QFileInfo # Added QFileInfo

class FileBrowserWidget(QWidget):
    # Signal emitted when a valid image file is selected
    fileSelected = pyqtSignal(str)
    # Signal emitted when any item (file or dir) is clicked within the target dir
    itemSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Determine and normalize the path to the 'images' directory ---
        self.target_images_path = self._find_images_directory() # This will be normcased/normpathed

        if not self.target_images_path or not os.path.isdir(self.target_images_path):
            error_path = self.target_images_path or 'Path not determined'
            QMessageBox.warning(self, "Directory Not Found",
                                f"Could not find or access the target directory:\n'{error_path}'."
                                f"\nPlease ensure 'images' exists relative to the project.\nFalling back to current directory.")
            # Fallback and normalize
            fallback_path = os.getcwd()
            self.target_images_path = os.path.normcase(os.path.normpath(fallback_path))

            if not os.path.isdir(self.target_images_path):
                 QMessageBox.critical(self, "Fatal Error", f"Fallback directory also not accessible: {self.target_images_path}")
                 # Widget might be unusable, consider disabling it or further action
                 pass # Allow initUI to proceed but it might show an empty view

        self.initUI()

    def _find_images_directory(self):
        """
        Tries to find the 'images' directory relative to this script file.
        Returns a normalized, case-normalized absolute path or None.
        """
        print("Attempting to find 'images' directory...")
        try:
            script_path = os.path.abspath(__file__)
            script_dir = os.path.dirname(script_path)
            cwd = os.getcwd()

            # Potential paths to check
            possible_relative_paths = [
                'images',                             # Relative to script dir
                os.path.join('..', 'images'),         # One level up from script dir
                os.path.join(cwd, 'images'),          # Relative to CWD
                os.path.join(cwd, 'image_viewer', 'images') # Common structure relative to CWD
            ]
            
            # Base directories to check relative paths against
            base_dirs = [script_dir, os.path.dirname(script_dir), cwd]

            checked_paths = set() # Avoid checking the same absolute path multiple times

            # Check relative to script dir and its parent first
            for base in base_dirs:
                for rel_path in ['images', os.path.join('..', 'images')]: # simplified relative checks here
                    potential_path = os.path.join(base, rel_path)
                    abs_path = os.path.abspath(potential_path)
                    if abs_path in checked_paths:
                        continue
                    checked_paths.add(abs_path)
                    print(f"Checking path: {abs_path}")
                    if os.path.isdir(abs_path):
                        normalized_path = os.path.normcase(os.path.normpath(abs_path))
                        print(f"Found images directory. Storing normalized path: {normalized_path}")
                        return normalized_path

            # Check relative to CWD as fallback
            for rel_path in ['images', os.path.join('image_viewer', 'images')]:
                 potential_path = os.path.join(cwd, rel_path)
                 abs_path = os.path.abspath(potential_path)
                 if abs_path in checked_paths:
                     continue
                 checked_paths.add(abs_path)
                 print(f"Checking path (relative to CWD): {abs_path}")
                 if os.path.isdir(abs_path):
                     normalized_path = os.path.normcase(os.path.normpath(abs_path))
                     print(f"Found images directory relative to CWD. Storing normalized path: {normalized_path}")
                     return normalized_path

            print("Warning: Could not automatically locate 'images' directory via common structures.")
            return None # Indicate failure

        except Exception as e:
            print(f"Error finding images directory: {e}")
            return None

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel("Image Browser")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.file_model = QFileSystemModel()

        print(f"Setting model root path to normalized path: {self.target_images_path}")
        # Set model root - QFileSystemModel handles path separators internally fine
        self.file_model.setRootPath(self.target_images_path)

        # Define allowed image extensions
        self.allowed_extensions = ["jpg", "jpeg", "png", "gif", "bmp"]
        name_filters = ["*." + ext for ext in self.allowed_extensions]
        self.file_model.setNameFilters(name_filters)
        self.file_model.setNameFilterDisables(False) # Show non-matching items greyed out

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)

        # Get the QModelIndex corresponding to the normalized root path
        root_index = self.file_model.index(self.target_images_path)
        if not root_index.isValid():
             print(f"ERROR: Root index for path '{self.target_images_path}' is invalid! Model may not see this path.")
             # Attempt to set view root to the model's rootPath() if specific index failed
             root_index = self.file_model.index(self.file_model.rootPath())
             if not root_index.isValid():
                  print(f"ERROR: Fallback root index is also invalid!")
                  # Handle this critical error - maybe disable tree view?
                  self.tree_view.setEnabled(False) # Disable interaction

        print(f"Setting tree view root index.")
        self.tree_view.setRootIndex(root_index) # Prevent navigation above this root

        self.tree_view.setAnimated(False)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        self.tree_view.setColumnWidth(0, 250) # Adjusted width slightly

        # Hide unnecessary columns
        self.tree_view.setColumnHidden(1, True) # Size
        self.tree_view.setColumnHidden(2, True) # Type
        self.tree_view.setColumnHidden(3, True) # Date Modified

        # Connect the click signal
        self.tree_view.clicked.connect(self._on_tree_clicked)

        layout.addWidget(self.tree_view)
        self.setLayout(layout)

        # Optional: Expand the root node initially if it's valid
        if root_index.isValid():
             self.tree_view.expand(root_index)


    def _on_tree_clicked(self, index: QModelIndex):
        if not index.isValid():
            print("Clicked invalid index.")
            return

        # Use the model to get file info - generally preferred
        file_info = self.file_model.fileInfo(index)
        # Get the absolute path using QFileInfo's method
        original_file_path = file_info.absoluteFilePath()

        print(f"\n--- Click Detected ---")
        print(f"Index valid: {index.isValid()}")
        print(f"Original File path: {original_file_path}")
        print(f"Is Dir (model): {self.file_model.isDir(index)}")
        print(f"Is Dir (file_info): {file_info.isDir()}")
        print(f"Suffix: {file_info.suffix()}")
        print(f"Target root path (stored, normalized): {self.target_images_path}")

        # Normalize the clicked path for comparison using Python's os.path functions
        norm_clicked_path = os.path.normcase(os.path.normpath(original_file_path))

        print(f"Normalized Clicked path: {norm_clicked_path}")
        print(f"Normalized Target path: {self.target_images_path}") # Already normalized

        # Compare normalized paths to ensure click is within the intended root
        # Use os.path.commonpath or simple startswith after normalization
        # Adding a separator to startswith check ensures "images_extra" isn't matched by "images"
        if norm_clicked_path.startswith(self.target_images_path):
             print("Path comparison successful (within target root).")
             # Emit the *original* non-normalized path for external use
             self.itemSelected.emit(original_file_path)
        else:
             # This might happen if the user somehow clicks an item filtered out
             # or if there's a symlink issue perhaps.
             print(f"WARNING: Normalized clicked path '{norm_clicked_path}' does not start with target root '{self.target_images_path}'. Ignoring.")
             return # Don't proceed if click seems outside the intended scope

        # Now check if it's a file of the correct type
        if file_info.isFile(): # Use QFileInfo's method
            print("Item is a file.")
            suffix = file_info.suffix().lower() # Get suffix and lowercase it
            print(f"File suffix (lower): '{suffix}'")

            if suffix in self.allowed_extensions:
                 print(f"File extension is allowed. Emitting fileSelected: {original_file_path}")
                 # Emit the *original* non-normalized path
                 self.fileSelected.emit(original_file_path)
            else:
                 print("File extension is NOT in allowed list.")
        else:
            print("Item is a directory.")