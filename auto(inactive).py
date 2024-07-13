import subprocess
import socket

def update_upgrade():
    subprocess.run(['sudo', 'apt-get', 'update'])
    subprocess.run(['sudo', 'apt-get', 'upgrade', '-y'])
    
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = 'Unable to determine IP Address'
    finally:
        s.close()
    return ip_address

update_upgrade()

ip_address = get_ip_address()
print(f'IP Address: {ip_address}')