# --- START OF MODIFIED watcher.py ---

import time
import os
import sys
import subprocess
import logging
import shutil  # For moving and copying files
from pathlib import Path # For easier path manipulation (especially home dir)
import psutil  # For process management
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# No need for datetime, time.strftime is sufficient

# --- Configuration ---
# Directory to watch for the incoming code.py file
# Uses pathlib to reliably find the user's Downloads folder
DOWNLOADS_FOLDER = Path.home() / "Downloads"

# Directory where the game runs and where stickkick.py should end up
# Set to "." if the watcher runs from the game's parent directory,
# otherwise use an absolute path like "/path/to/your/game/folder"
GAME_FOLDER = Path(".") # Or use Path("/path/to/your/game/folder")

TARGET_FILENAME = "code.py"
NEW_FILENAME = "stickkick.py"
HISTORY_FOLDER_NAME = "history" # Name of the backup directory within GAME_FOLDER

# How to identify the game process to terminate (CHANGE THIS!)
GAME_SCRIPT_FILENAME = "stickkick.py" # The filename of your *CURRENTLY RUNNING* game script

# Setup basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# --- Functions ---

def find_and_terminate_game_process(script_name_to_find):
    """Finds and terminates Python processes running the specified script."""
    terminated_count = 0
    # Ensure we're comparing against absolute paths if possible
    try:
        # Try to resolve the game script path relative to the GAME_FOLDER
        game_script_path = GAME_FOLDER.resolve() / script_name_to_find
    except OSError:
         # Fallback if GAME_FOLDER is invalid somehow
         game_script_path = Path(script_name_to_find) # Use relative path as fallback

    logging.info(f"Searching for processes running a script like: '{script_name_to_find}' or '{game_script_path}'")

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            p_info = proc.info
            if not p_info['cmdline']: # Skip processes with empty cmdline
                 continue

            # Check if it's a python process
            # More robust check for python interpreter variations
            is_python_proc = ('python' in p_info.get('name','').lower() or
                              (sys.executable and p_info.get('exe','') and Path(p_info['exe']) == Path(sys.executable)))

            if is_python_proc:
                 # Check if the target script name or full path is in the command line arguments
                 cmdline_str = ' '.join(p_info['cmdline'])
                 script_found_in_cmd = False
                 # Iterate through arguments for a more precise match
                 for arg in p_info['cmdline'][1:]: # Skip the python executable itself
                      # Simple check first
                      if script_name_to_find in arg:
                          # Try resolving paths for a better match
                          try:
                              arg_path = Path(arg)
                              if arg_path.name == script_name_to_find:
                                   # Resolve both if possible for comparison
                                   try:
                                       if arg_path.resolve() == game_script_path:
                                           script_found_in_cmd = True
                                           break
                                   except: # Handle resolve errors
                                        # Fallback to name comparison if resolve fails
                                       if arg_path.name == script_name_to_find:
                                            script_found_in_cmd = True
                                            break
                          except: # Handle errors creating Path object from arg
                               if script_name_to_find in arg: # Basic string check as last resort
                                    script_found_in_cmd = True
                                    break

                 if script_found_in_cmd:
                    logging.info(f"Found game process: PID={proc.pid}, CmdLine='{cmdline_str}'")
                    try:
                        p = psutil.Process(proc.pid)
                        p.terminate() # Send SIGTERM (graceful shutdown)
                        logging.info(f"Sent terminate signal to PID {proc.pid}.")
                        # Optional: Wait a bit and check if it exited, then force kill
                        try:
                            p.wait(timeout=3)
                            logging.info(f"Process PID {proc.pid} terminated gracefully.")
                        except psutil.TimeoutExpired:
                            logging.warning(f"Process PID {proc.pid} did not terminate gracefully after 3s. Forcing kill.")
                            p.kill()
                            p.wait()
                            logging.info(f"Process PID {proc.pid} killed.")
                        terminated_count += 1
                    except psutil.NoSuchProcess:
                        logging.warning(f"Process PID {proc.pid} already exited.")
                    except psutil.AccessDenied:
                        logging.error(f"Permission denied to terminate PID {proc.pid}. Try running watcher as administrator/root?")
                    except Exception as e:
                        logging.error(f"Error terminating PID {proc.pid}: {e}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass # Ignore processes that disappeared or we can't access
        except Exception as e:
            # Reduce noise for common inspection errors like missing cmdline
            if 'cmdline' not in str(e):
                logging.error(f"Error inspecting process {proc.pid if proc else 'N/A'}: {e}")


    if terminated_count == 0:
        logging.warning(f"No running game process found matching script '{script_name_to_find}'.")
    return terminated_count > 0

def run_new_script(script_path, working_directory):
    """Runs the specified Python script."""
    try:
        # Ensure paths are strings for subprocess
        script_path_str = str(script_path)
        working_dir_str = str(working_directory)

        if not script_path.exists():
             logging.error(f"Error: Script to run '{script_path_str}' does not exist.")
             return False

        logging.info(f"Attempting to run '{script_path_str}' in '{working_dir_str}'...")
        # Use sys.executable to ensure the same python interpreter is used
        # Run in the background using Popen, set working directory
        process = subprocess.Popen([sys.executable, script_path_str], cwd=working_dir_str)
        logging.info(f"Started '{script_path.name}' with PID {process.pid}.")
        return True
    except Exception as e:
        logging.error(f"Error running '{script_path.name}': {e}")
        return False

class CodeFileHandler(FileSystemEventHandler):
    """Handles file system events in the Downloads folder."""
    def __init__(self, target_filename, new_filename, game_folder, game_script, history_folder_name):
        self.target_filename = target_filename
        self.new_filename = new_filename
        self.game_folder = game_folder # This is a Path object
        self.game_script = game_script
        self.history_folder = game_folder / history_folder_name # Path object for history
        self.final_script_path = self.game_folder / self.new_filename
        # Simple debounce: store timestamp of last successful processing
        self.last_processed_time = 0
        self.debounce_seconds = 3 # Slightly shorter debounce


    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return

        current_time = time.time()
        if current_time - self.last_processed_time < self.debounce_seconds:
            # logging.info(f"Debouncing: Ignoring event for {event.src_path}")
            return

        source_filepath = Path(event.src_path)
        filename = source_filepath.name

        if filename == self.target_filename:
            logging.info(f"Detected target file: {source_filepath}")

            # --- Stability Check ---
            try:
                # Wait a short moment for file write to potentially finish
                time.sleep(0.5) # Increased slightly for potentially larger files
                if not source_filepath.exists() or source_filepath.stat().st_size == 0:
                    if not source_filepath.exists():
                         logging.warning(f"'{filename}' disappeared before processing. Ignoring.")
                         return
                    else:
                         # Decide if empty files are valid - proceed but warn
                         logging.warning(f"'{filename}' is empty, proceeding anyway.")

            except FileNotFoundError:
                 logging.warning(f"'{filename}' disappeared immediately after detection. Ignoring.")
                 return
            except Exception as e:
                 logging.error(f"Error checking file stability for {source_filepath}: {e}")
                 return

            # --- Define Paths ---
            final_dest_path = self.final_script_path # e.g., ./stickkick.py

            # --- Backup, Move, Rename Logic ---
            try:
                # Ensure game folder exists
                self.game_folder.mkdir(parents=True, exist_ok=True)

                # --- Backup Step ---
                # Check if the file we are about to replace exists
                if final_dest_path.exists():
                    try:
                        # Ensure history folder exists
                        self.history_folder.mkdir(parents=True, exist_ok=True)

                        # Generate timestamped backup filename (YYYY-MM-DD HH-MM-SS filename.ext)
                        timestamp_str = time.strftime("%Y-%m-%d %H-%M-%S")
                        backup_filename = f"{timestamp_str} {self.new_filename}"
                        backup_dest_path = self.history_folder / backup_filename

                        logging.info(f"Backing up existing '{final_dest_path.name}' to '{backup_dest_path}'")
                        # Use copy2 to preserve metadata like modification time
                        shutil.copy2(str(final_dest_path), str(backup_dest_path))

                    except Exception as backup_error:
                        # Log the error but continue with the replacement process
                        logging.error(f"Failed to backup '{final_dest_path.name}': {backup_error}")
                # --- End Backup Step ---


                # --- Move and Overwrite Step ---
                # Move the downloaded file directly to the final destination, overwriting the old one
                logging.info(f"Moving '{source_filepath}' to '{final_dest_path}' (overwriting if exists)")
                # shutil.move handles overwriting automatically and works across different filesystems/drives
                shutil.move(str(source_filepath), str(final_dest_path)) # Requires string paths


                # --- Process Termination and Execution ---
                # 3. Terminate the old game
                logging.info("Attempting to terminate the current game process...")
                # Use NEW_FILENAME here as we are targeting the script that *should* be running
                terminated = find_and_terminate_game_process(self.new_filename)
                # Add a small delay to allow termination, especially if termination was forced
                if terminated:
                    time.sleep(1.5)
                else:
                    # If no game was found running, wait less time.
                    time.sleep(0.5)

                # 4. Run the new script
                logging.info("Attempting to run the new script...")
                if run_new_script(final_dest_path, self.game_folder):
                    self.last_processed_time = time.time() # Update timestamp on success
                else:
                    logging.error("Failed to start the new script.")


            except FileNotFoundError:
                # This could happen if the source file is deleted between detection and move
                 logging.error(f"Error: '{source_filepath.name}' was moved or deleted before processing.")
            except PermissionError as e:
                 logging.error(f"Permission error during file operations: {e}. Check permissions for Downloads, Game, and History folders.")
            except Exception as e:
                 logging.error(f"An error occurred during backup/move/run: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    # Resolve absolute paths for clarity and robustness
    watch_path = DOWNLOADS_FOLDER.resolve()
    game_path = GAME_FOLDER.resolve()
    history_path = game_path / HISTORY_FOLDER_NAME

    logging.info(f"Starting watcher for folder: {watch_path}")
    logging.info(f"Game folder set to: {game_path}")
    logging.info(f"Backup history folder set to: {history_path}")
    logging.info(f"Watching for file: '{TARGET_FILENAME}'")
    logging.info(f"Will move to game folder as: '{NEW_FILENAME}'")
    logging.info(f"Existing '{NEW_FILENAME}' will be backed up before replacement.")
    logging.info(f"Will terminate processes running script like: '{NEW_FILENAME}'") # Changed GAME_SCRIPT_FILENAME to NEW_FILENAME for consistency

    # Validate paths
    if not watch_path.is_dir():
        logging.error(f"Error: Watch folder does not exist or is not a directory: {watch_path}")
        sys.exit(1)
    # We attempt to create game_path and history_path later if they don't exist.

    # --- ADDED: Initial run attempt ---
    initial_script_path = game_path / NEW_FILENAME
    logging.info("-" * 20) # Separator
    if initial_script_path.exists():
        logging.info(f"Attempting initial run of '{initial_script_path.name}'...")
        run_new_script(initial_script_path, game_path)
        # Add a small delay maybe, though run_new_script runs it in background
        time.sleep(1.0)
    else:
        logging.warning(f"Initial script '{initial_script_path.name}' not found in game folder. Skipping initial run.")
    logging.info("-" * 20) # Separator
    # --- END ADDED ---


    event_handler = CodeFileHandler(
        target_filename=TARGET_FILENAME,
        new_filename=NEW_FILENAME,
        game_folder=game_path,
        game_script=NEW_FILENAME, # Pass NEW_FILENAME as the script to terminate
        history_folder_name=HISTORY_FOLDER_NAME # Pass the name
    )
    observer = Observer()
    # Watch the Downloads folder, non-recursively
    observer.schedule(event_handler, str(watch_path), recursive=False) # watchdog needs string path

    observer.start()
    logging.info("Watcher started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping watcher...")
        observer.stop()
    except Exception as e:
        logging.error(f"An unexpected error occurred in the main loop: {e}")
        observer.stop()

    observer.join()
    logging.info("Watcher stopped.")

# --- END OF MODIFIED watcher.py ---