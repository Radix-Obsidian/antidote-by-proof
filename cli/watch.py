"""Watchdog-based file watcher for continuous scanning."""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from engine.ast_parser import scan_file
from engine.patch_generator import generate_patch
from engine.logger import log
from events.emitter import emit


class _Handler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self._process(event.src_path)

    def on_created(self, event):
        if event.src_path.endswith(".py"):
            self._process(event.src_path)

    def _process(self, filepath: str):
        try:
            findings = scan_file(filepath)
            for finding in findings:
                with open(filepath) as f:
                    lines = f.readlines()
                patch = generate_patch(finding, lines)
                event_path = emit(finding, patch)
                log.info(
                    f"{finding['severity']}: {finding['function']} "
                    f"at {filepath}:{finding['line']} -> {event_path}"
                )
        except Exception as e:
            log.error(f"Error processing {filepath}: {e}")


def start_watch(directory: str):
    """Start watching a directory for Python file changes."""
    observer = Observer()
    observer.schedule(_Handler(), directory, recursive=True)
    observer.start()
    log.info(f"Watching {directory} for unprotected routes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
