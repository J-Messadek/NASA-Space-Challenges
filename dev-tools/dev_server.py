#!/usr/bin/env python3
"""
Development environment with auto-reload + auto-format + linting
Does everything automatically when you save files
"""

import subprocess
import sys
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class DevEnvironmentHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_processed = {}  # Track last modification time to avoid loops
        self.start_main()

    def start_main(self):
        """Start the main.py process"""
        if self.process:
            self.process.terminate()
            self.process.wait()

        print("\n" + "=" * 50)
        print("Starting main.py...")
        print("=" * 50)

        self.process = subprocess.Popen([sys.executable, "main.py"])

    def format_and_check_file(self, file_path):
        """Format and check a Python file"""
        try:
            # Format with black
            result = subprocess.run(
                [sys.executable, "-m", "black", str(file_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"Formatted: {file_path.name}")
            else:
                print(f"Black failed: {result.stderr}")

            # Sort imports with isort
            result = subprocess.run(
                [sys.executable, "-m", "isort", str(file_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"Sorted imports: {file_path.name}")

            # Check with flake8
            result = subprocess.run(
                [sys.executable, "-m", "flake8", str(file_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"Code check passed: {file_path.name}")
            else:
                print(f"Code issues found: {result.stdout}")

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process Python files
        if not file_path.suffix == ".py":
            return

        # Skip if we just processed this file (avoid infinite loops)
        current_time = time.time()
        if file_path in self.last_processed:
            if current_time - self.last_processed[file_path] < 1.0:  # 1 second buffer
                return

        self.last_processed[file_path] = current_time

        print(f"\nProcessing: {file_path.name}")

        # Format and check the file
        self.format_and_check_file(file_path)

        # Restart main.py if it's not the dev server itself
        if file_path.name != "dev_server.py":
            print("Restarting application...")
            self.start_main()


def main():
    """Start the development environment"""
    print("Development Environment Starting...")
    print("Auto-reload + Auto-format + Code checking enabled")
    print("Watching for changes in Python files...")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    event_handler = DevEnvironmentHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping development environment...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()

    observer.join()


if __name__ == "__main__":
    main()