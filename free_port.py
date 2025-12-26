import socket
import os
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 5000))

if result == 0:
    print("Port 5000 is in use")

    # Try to identify and kill process (Unix-like)
    try:
        import subprocess
        # Get PID using port 5000
        output = subprocess.check_output(['netstat', '-tulpn'], text=True)
        for line in output.split('\n'):
            if ':5000' in line:
                parts = line.split()
                if len(parts) >= 7:
                    pid = parts[6].split('/')[0]
                    print(f"Process using port: PID {pid}")
                    # Kill it
                    os.kill(int(pid), 9)
                    print(f"Killed process {pid}")
                    break
    except:
        print("Could not auto-kill. Manually stop what's using port 5000")

    print("Now try: flask run")
else:
    print("Port 5000 is free")
    print("Start Flask with: flask run")
