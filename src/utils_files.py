import os


class FileUtils:
    """
    Utility class for handling file paths and directory-related operations.
    """

    @staticmethod
    def get_path(element: str) -> str:
        """
        Constructs an absolute path for the specified element relative to the current
        file's directory.

        Args:
            element (str): The name of the file or directory for which the path is being
            constructed. This should be a relative path from the current file's location.

        Returns:
            str: The absolute path to the specified element.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, element)
        return path

    @staticmethod
    def get_latest_file(folder: str) -> str | None:
        """
        Retrieve the most recently modified file in a directory.

        Args:
            folder (str): Path to the target directory.

        Returns:
            str | None: Full path to the most recent file, or None if the directory is
            empty.
        """
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]
        return max(files, key=os.path.getmtime) if files else None
