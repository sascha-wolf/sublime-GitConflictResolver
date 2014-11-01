import os

from . import settings
from . import util


class GitMixin:
    def git_command(self, command, repo=None):
        """Executes a git command. Expects an array as command argument,
        with each subcommand, option, argument being a own element.

        The repo argument can be used to specify the folder in which the
        command should be executed."""
        return util.execute_command(
            [settings.get('git_path')] + command,
            working_dir=repo
        )

    def git_executable_available(self):
        try:
            self.git_command([])  # Try to execute a naked "git"
        except FileNotFoundError:
            return False
        else:
            return True

    def determine_git_repo(self):
        """Returns the root git repository path for the current view.
        If the view has no file path it returns the root path for the first
        open folder.

        Returns None if both methods are unsuccessfull."""
        open_view_path = self.window.active_view().file_name()
        open_folders = self.window.folders()

        working_dir = None
        if open_view_path:
            # Remove the traling filename, we just need the folder
            working_dir = os.path.dirname(open_view_path)
        elif open_folders:
            working_dir = open_folders[0]

        # Get git top-level folder
        if working_dir:
            working_dir = self.git_command(
                ["rev-parse", "--show-toplevel"],
                repo=working_dir)

        return working_dir
