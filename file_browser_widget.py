import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QFileSystemModel, QTreeView, QMessageBox)
from PyQt5.QtCore import Qt, QDir, pyqtSignal, QModelIndex, QFileInfo # Added QFileInfo

class FileBrowserWidget(QWidget):
    fileSelected = pyqtSignal(str)
    itemSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.target_images_path = self._find_images_directory() 

        if not self.target_images_path or not os.path.isdir(self.target_images_path):
            error_path = self.target_images_path or 'Path not determined'
            QMessageBox.warning(self, "Directory Not Found",
                                f"Could not find or access the target directory:\n'{error_path}'."
                                f"\nPlease ensure 'images' exists relative to the project.\nFalling back to current directory.")
            fallback_path = os.getcwd()
            self.target_images_path = os.path.normcase(os.path.normpath(fallback_path))

            if not os.path.isdir(self.target_images_path):
                 QMessageBox.critical(self, "Fatal Error", f"Fallback directory also not accessible: {self.target_images_path}")
                 pass

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

            possible_relative_paths = [
                'images',                            
                os.path.join('..', 'images'),        
                os.path.join(cwd, 'images'),          
                os.path.join(cwd, 'image_viewer', 'images') 
            ]
            
            base_dirs = [script_dir, os.path.dirname(script_dir), cwd]

            checked_paths = set() 

            for base in base_dirs:
                for rel_path in ['images', os.path.join('..', 'images')]: 
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
            return None 

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
        self.file_model.setRootPath(self.target_images_path)

        self.allowed_extensions = ["jpg", "jpeg", "png", "gif", "bmp"]
        name_filters = ["*." + ext for ext in self.allowed_extensions]
        self.file_model.setNameFilters(name_filters)
        self.file_model.setNameFilterDisables(False) 

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)

        root_index = self.file_model.index(self.target_images_path)
        if not root_index.isValid():
             print(f"ERROR: Root index for path '{self.target_images_path}' is invalid! Model may not see this path.")
             root_index = self.file_model.index(self.file_model.rootPath())
             if not root_index.isValid():
                  print(f"ERROR: Fallback root index is also invalid!")
                  self.tree_view.setEnabled(False) 

        print(f"Setting tree view root index.")
        self.tree_view.setRootIndex(root_index)

        self.tree_view.setAnimated(False)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        self.tree_view.setColumnWidth(0, 250) 

        self.tree_view.setColumnHidden(1, True) 
        self.tree_view.setColumnHidden(2, True) 
        self.tree_view.setColumnHidden(3, True) 

        self.tree_view.clicked.connect(self._on_tree_clicked)

        layout.addWidget(self.tree_view)
        self.setLayout(layout)

        if root_index.isValid():
             self.tree_view.expand(root_index)


    def _on_tree_clicked(self, index: QModelIndex):
        if not index.isValid():
            print("Clicked invalid index.")
            return

        file_info = self.file_model.fileInfo(index)
        original_file_path = file_info.absoluteFilePath()

        print(f"\n--- Click Detected ---")
        print(f"Index valid: {index.isValid()}")
        print(f"Original File path: {original_file_path}")
        print(f"Is Dir (model): {self.file_model.isDir(index)}")
        print(f"Is Dir (file_info): {file_info.isDir()}")
        print(f"Suffix: {file_info.suffix()}")
        print(f"Target root path (stored, normalized): {self.target_images_path}")

        norm_clicked_path = os.path.normcase(os.path.normpath(original_file_path))

        print(f"Normalized Clicked path: {norm_clicked_path}")
        print(f"Normalized Target path: {self.target_images_path}")

        if norm_clicked_path.startswith(self.target_images_path):
             print("Path comparison successful (within target root).")
             self.itemSelected.emit(original_file_path)
        else:
             print(f"WARNING: Normalized clicked path '{norm_clicked_path}' does not start with target root '{self.target_images_path}'. Ignoring.")
             return 

        if file_info.isFile(): 
            print("Item is a file.")
            suffix = file_info.suffix().lower() 
            print(f"File suffix (lower): '{suffix}'")

            if suffix in self.allowed_extensions:
                 print(f"File extension is allowed. Emitting fileSelected: {original_file_path}")
                 self.fileSelected.emit(original_file_path)
            else:
                 print("File extension is NOT in allowed list.")
        else:
            print("Item is a directory.")