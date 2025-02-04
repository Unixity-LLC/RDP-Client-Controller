import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from pathlib import Path
import platform
import time

# Load environment variables from user.config.env
env_path = Path(__file__).parent / "user.config.env"
load_dotenv(env_path)

USERNAME = os.getenv("USERNAME", "").strip()
PASSWORD = os.getenv("PASSWORD", "").strip()
HOSTNAME = os.getenv("HOSTNAME", "").strip()

print("Loaded ENV Variables:")
print(f"USERNAME: {USERNAME}")
print(f"PASSWORD: {'*' * len(PASSWORD)}")  # Mask password for security
print(f"HOSTNAME: {HOSTNAME}")

# Function to check OS and xfreerdp installation
def check_system():
    system = platform.system()

    if system == "Linux":
        try:
            subprocess.run(["which", "xfreerdp"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            show_error("xfreerdp is not installed.\nPlease install it with:\n\nsudo apt install freerdp2-x11")
            return False
    return True

# Function to show error messages in a GUI window
def show_error(message):
    error_root = tk.Tk()
    error_root.withdraw()  # Hide the main window
    messagebox.showerror("Error", message)
    error_root.destroy()

def connect_rdp(root):
    """Starts an RDP session and restarts the GUI after disconnect."""

    if not USERNAME or not PASSWORD or not HOSTNAME:
        show_error("Missing USERNAME, PASSWORD, or HOSTNAME in user.config.env")
        return

    rdp_command = f"xfreerdp /u:{USERNAME} /p:{PASSWORD} /v:{HOSTNAME} /w:1920 /h:1080 /f /multimon /cert-ignore"

    print(f"Running command: {rdp_command}")

    try:
        root.destroy()  # Close Tkinter GUI before launching RDP
        print("Tkinter window closed.")

        # Start RDP session
        process = subprocess.Popen(rdp_command, shell=True)
        process.wait()  # Wait for RDP to close

        print("RDP session ended. Restarting application in 5 seconds...")
        time.sleep(5)  # Pause before restarting

        launch_gui()  # Restart GUI after RDP disconnects

    except Exception as e:
        show_error(f"Error launching RDP:\n{str(e)}")

# GUI Setup
def launch_gui():
    """Creates and launches the Tkinter GUI."""
    root = tk.Tk()
    root.title("Raspberry Pi RDP Connector")
    root.geometry("300x200")

    label = tk.Label(root, text="Press 'Connect' or Enter to start RDP", font=("Arial", 12))
    label.pack(pady=20)

    connect_button = tk.Button(root, text="Connect", command=lambda: connect_rdp(root), font=("Arial", 14))
    connect_button.pack(pady=10)

    root.bind("<Return>", lambda event: connect_rdp(root))
    root.mainloop()

# Main Execution
if __name__ == "__main__":
    if check_system():
        launch_gui()