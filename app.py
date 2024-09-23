import socket
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from zeroconf import ServiceInfo, Zeroconf
from audio_processes import get_process_names, get_volume, set_volume, get_master_volume, set_master_volume
import time

volume_lock = threading.Lock()

processNames = list(set([x.split(".")[0] for x in get_process_names() if "ShellExperienceHost" not in x]))
#print(processNames)

slider_data = {
    'names': ['master'] + processNames,
    'volumes': [get_master_volume()] + [get_volume(x) for x in processNames]
}
#print(slider_data)

UDP_PORT = 8081
UDP_IP = '0.0.0.0'

class MyRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_GET(self):
        if self.path == "/bindapp":
            response_content = json.dumps(slider_data)
            print(slider_data)
            self._send_response(response_content)
        elif self.path == "/address":
            response_content = get_local_ip()
            self._send_response(response_content)
            print(f"inviato {response_content}")
        else:
            self._send_response(json.dumps({'error': 'Invalid endpoint'}), status=404)

def start_http_server():
    httpd = HTTPServer(('0.0.0.0', 80), MyRequestHandler)
    print("HTTP server in esecuzione su porta 80")
    httpd.serve_forever()

def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"UDP server in ascolto su porta {UDP_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8')
        try:
            json_data = json.loads(message)
            print(f"Ricevuto da {addr}: {json_data}")
            slider_name = json_data['slider']
            new_value = json_data['value']
            if slider_name in slider_data['names']:
                index = slider_data['names'].index(slider_name)
                slider_data['volumes'][index] = new_value
                print(f"Aggiornato {slider_name} con valore {new_value}")
            if slider_name == 'master':
                with volume_lock:
                    set_master_volume(new_value)
            else:
                set_volume(slider_name, new_value)
        except json.JSONDecodeError:
            print("Errore nella decodifica del messaggio UDP")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        print(f"Errore nel recupero dell'indirizzo IP: {e}")
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def start_mdns_service():
    desc = {'path': '/'}
    info = ServiceInfo(
        "_http._tcp.local.",
        "pcvolume._http._tcp.local.",
        addresses=[socket.inet_aton(get_local_ip())],
        port=80,
        properties=desc,
        server="pcvolume.local.",
    )
    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    print("Servizio mDNS registrato")

def update_slider_data():
    global slider_data
    while True:
        new_processNames = list(set([x.split(".")[0] for x in get_process_names() if "ShellExperienceHost" not in x]))
        new_volumes = [get_master_volume()] + [get_volume(x) for x in new_processNames]
        if new_processNames != slider_data['names'][1:] or new_volumes != slider_data['volumes']:
            slider_data = {
                'names': ['master'] + new_processNames,
                'volumes': new_volumes
            }
            print(f"Dati aggiornati: {slider_data}")
        time.sleep(10)

if __name__ == "__main__":
    start_mdns_service()

    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()

    udp_thread = threading.Thread(target=udp_listener)
    udp_thread.daemon = True
    udp_thread.start()

    update_thread = threading.Thread(target=update_slider_data)
    update_thread.daemon = True
    update_thread.start()

    while True:
        time.sleep(1)
