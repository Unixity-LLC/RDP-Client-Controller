import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from pathlib import Path
import platform

# Load environment variables from user.config.env
env_path = Path(__file__).parent / "user.config.env"
load_dotenv(env_path)

USERNAME = os.getenv("USERNAME", "")
PASSWORD = os.getenv("PASSWORD", "")
HOSTNAME = os.getenv("HOSTNAME", "")

print("Loaded ENV Variables:")
print(f"USERNAME: {USERNAME}")
print(f"PASSWORD: {PASSWORD}")
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
    exit(1)


# Function to initiate RDP connection
def connect_rdp():
    if not USERNAME or not PASSWORD or not HOSTNAME:
        show_error("Missing USERNAME, PASSWORD, or HOSTNAME in user.config.env")
        return

    rdp_command = f"xfreerdp /u:{USERNAME} /p:{PASSWORD} /v:{HOSTNAME} /f /multimon"

    print(f"Running command: {rdp_command}")  # Debugging output

    try:
        process = subprocess.Popen(rdp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        stdout_output = stdout.decode().strip()
        stderr_output = stderr.decode().strip()

        print("STDOUT:", stdout_output)
        print("STDERR:", stderr_output)

        if stderr_output:
            show_error(f"RDP Connection Error:\n{stderr_output}")

    except Exception as e:
        show_error(f"Error launching RDP:\n{str(e)}")


# GUI Setup
def launch_gui():
    root = tk.Tk()
    root.title("Raspberry Pi RDP Connector")
    root.geometry("300x200")

    # Label
    label = tk.Label(root, text="Press 'Connect' or Enter to start RDP", font=("Arial", 12))
    label.pack(pady=20)

    # Button
    connect_button = tk.Button(root, text="Connect", command=connect_rdp, font=("Arial", 14))
    connect_button.pack(pady=10)

    # Bind Enter key to Connect function
    root.bind("<Return>", lambda event: connect_rdp())

    root.mainloop()


# Main Execution
if __name__ == "__main__":
    if check_system():
        launch_gui()