import os
import threading
import time
import Pyro4
from os.path import isfile, join


@Pyro4.behavior(instance_mode="single")
class FileServer(object):
    def __init__(self):
        self.storage_path = './storage/'
        # Centralized Heartbeat
        # threading.Thread(target=self.thread_send_heartbeat_to_central, kwargs={'interval_time': 1}).start()
        # All to All Heartbeat
        self.services = {}
        self.register_service("Failure Detector Service", "PYRONAME:failuredetectorserver@localhost:7777")
        self.register_service("Greet Service", "PYRONAME:greetserver@localhost:7777")
        self.current_services_heartbeat = {}
        self.last_services_heartbeat = {}
        threading.Thread(target=self.thread_check_services_heartbeat, kwargs={'interval_time': 3}).start()
        threading.Thread(target=self.thread_send_multiple_heartbeat, kwargs={'interval_time': 1}).start()

    def thread_send_multiple_heartbeat(self, interval_time):
        sequence_number = 0
        while True:
            sequence_number += 1
            for service_name in self.services:
                service_proxy = Pyro4.Proxy(self.services[service_name])
                try:
                    service_proxy.send_heartbeat("File Service", sequence_number)
                except Pyro4.errors.CommunicationError:
                    print("Gagal mengirim heartbeat ke " + service_name)
                except Pyro4.errors.PyroError:
                    print("Gagal mengirim heartbeat ke " + service_name)
            time.sleep(interval_time)

    def thread_check_services_heartbeat(self, interval_time):
        while True:
            for service_name in list(self.current_services_heartbeat):
                if self.last_services_heartbeat.get(service_name, False):
                    if self.last_services_heartbeat[service_name] == self.current_services_heartbeat[service_name]:
                        print(service_name + " sedang off")
                    else:
                        self.last_services_heartbeat[service_name] = self.current_services_heartbeat[service_name]
                        print(service_name + " sedang berjalan")
                else:
                    self.last_services_heartbeat[service_name] = self.current_services_heartbeat[service_name]
                    print(service_name + " telah terdaftar")
            time.sleep(interval_time)

    def register_service(self, service_name, service_url):
        self.services[service_name] = service_url
        return self.services

    def send_heartbeat(self, service_name, sequence_number):
        self.current_services_heartbeat[service_name] = sequence_number

    def thread_send_heartbeat_to_central(self, interval_time):
        uri = "PYRONAME:failuredetectorserver@localhost:7777"
        sequence_number = 0
        while True:
            sequence_number += 1
            failure_detector_server = Pyro4.Proxy(uri)
            try:
                failure_detector_server.send_heartbeat("fileserver", sequence_number)
            except Pyro4.errors.CommunicationError:
                print("Gagal mengirim heartbeat")
            except Pyro4.errors.PyroError:
                print("Gagal mengirim heartbeat")
            time.sleep(interval_time)

    def upload_file(self, file_name, file_content):
        print(f"Mengupload {file_name}")
        if os.path.exists(self.storage_path+file_name):
            return f"File bernama {file_name} sudah ada"
        else:
            with open(self.storage_path+file_name, "w+") as file:
                file.write(file_content)
            return f"File bernama {file_name} telah dibuat"

    def get_all_files_name(self):
        files = [f for f in os.listdir(self.storage_path) if isfile(join(self.storage_path, f))]
        return files

    def read_file_by_name(self, filename):
        is_file_exist = os.path.exists(self.storage_path+filename)
        if is_file_exist:
            with open(self.storage_path+filename, "r") as file:
                content = file.read()
            return content
        else:
            return f"File bernama {filename} tidak ditemukan"

    def delete_file_by_name(self, filename):
        is_file_exist = os.path.exists(self.storage_path + filename)
        if is_file_exist:
            os.remove(self.storage_path+filename)
            return f"File bernama {filename} berhasil dihapus"
        else:
            return f"File bernama {filename} tidak ditemukan"

    def update_file(self, file_name, file_content):
        is_file_exist = os.path.exists(self.storage_path + file_name)
        if is_file_exist:
            with open(self.storage_path+file_name, "w") as file:
                file.write(file_content)
            return f"File bernama {file_name} berhasil diupdate"
        else:
            return f"File bernama {file_name} tidak ditemukan"
