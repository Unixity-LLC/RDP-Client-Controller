import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from pathlib import Path
import socket
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
def get_local_ip():
    """Get the local IP address of the Raspberry Pi."""
    try:
        # Create a dummy socket to determine the IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS (does not send actual data)
        local_ip = s.getsockname()[0]  # Get local IP address
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def launch_gui():
    """Creates and launches the Tkinter GUI."""
    root = tk.Tk()
    root.title("Connection Client")
    root.geometry("300x200")

    # ✅ Disable Close (X) Button → Reboots the system
    root.protocol("WM_DELETE_WINDOW", handle_close)

    # ✅ Disable Minimize & Maximize Buttons
    root.attributes("-alpha", True)  # Removes minimize/maximize buttons
    root.attributes("-topmost", True)  # Keeps the window always on top

    # ✅ Prevent Resizing
    root.resizable(False, False)

    label = tk.Label(root, text=f"Welcome, {USERNAME}", font=("Arial", 12))
    label.pack(pady=20)

    connect_button = tk.Button(root, text="Connect", command=lambda: connect_rdp(root), font=("Arial", 14))
    connect_button.pack(pady=10)

    # ✅ Display device's LOCAL IP at the bottom in small text
    local_ip = get_local_ip()
    ip_label = tk.Label(root, text=f"Device: {local_ip}", font=("Arial", 8), fg="gray")
    ip_label.pack(side="bottom", pady=5)

    root.bind("<Return>", lambda event: connect_rdp(root))
    root.mainloop()

def handle_close():
    """Handles attempts to close the application."""
    print("User attempted to close the application! Restarting system...")
    subprocess.run(["sudo", "reboot"])  # Force restart the system

# Main Execution
if __name__ == "__main__":
    if check_system():
        launch_gui()