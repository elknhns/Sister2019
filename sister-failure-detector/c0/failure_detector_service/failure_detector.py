import Pyro4
import time
import threading


@Pyro4.behavior(instance_mode="single")
class FailureDetectorServer:
    def __init__(self):
        self.services = {}
        self.services_last_status = {}
        self.register_service("File Service", "PYRONAME:fileserver@localhost:7777")
        self.register_service("Greet Service", "PYRONAME:greetserver@localhost:7777")
        # Ping-ACK
        # threading.Thread(target=self.thread_ping_services, kwargs={'interval_time': 3}).start()
        # Centralized Heartbeat
        self.last_services_heartbeat = {}
        self.current_services_heartbeat = {}
        # threading.Thread(target=self.thread_check_services_heartbeat, kwargs={'interval_time': 3}).start()
        # All to all Heartbeat
        threading.Thread(target=self.thread_check_services_heartbeat, kwargs={'interval_time': 3}).start()
        threading.Thread(target=self.thread_send_multiple_heartbeat, kwargs={'interval_time': 1}).start()

    def thread_send_multiple_heartbeat(self, interval_time):
        sequence_number = 0
        while True:
            sequence_number += 1
            for service_name in self.services:
                service_proxy = Pyro4.Proxy(self.services[service_name])
                try:
                    service_proxy.send_heartbeat("Failure Detector Service", sequence_number)
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
                        print(service_name + " sedang down")
                    else:
                        self.last_services_heartbeat[service_name] = self.current_services_heartbeat[service_name]
                        print(service_name + " sedang berjalan")
                else:
                    self.last_services_heartbeat[service_name] = self.current_services_heartbeat[service_name]
                    print(service_name + " telah terdaftar")
            time.sleep(interval_time)

    def send_heartbeat(self, service_name, sequence_number):
        self.current_services_heartbeat[service_name] = sequence_number

    def thread_ping_services(self, interval_time):
        while True:
            self.ping_services()
            time.sleep(interval_time)

    def ping_services(self):
        for service_name in list(self.services):
            # For debug only:
            # print(f'Ping {service_name}')
            is_service_available = self.__ping_service(self.services[service_name])
            if self.services_last_status[service_name] != is_service_available:
                if not is_service_available:
                    print(f'{service_name} sedang off')
                else:
                    print(f'{service_name} sedang menyala')
            self.services_last_status[service_name] = is_service_available
        return self.services_last_status

    def remove_service(self, service_name):
        self.services.pop(service_name)
        self.services_last_status.pop(service_name)
        return list(self.services.keys())

    def get_all_services_name(self):
        return list(self.services.keys())

    def register_service(self, service_name, service_url):
        self.services[service_name] = service_url
        self.services_last_status[service_name] = False
        return self.services

    def __ping_service(self, service_url):
        try:
            connection = Pyro4.Proxy(service_url)
            connection._pyroBind()
            return True
        except Pyro4.errors.NamingError:
            return False
        except Pyro4.errors.CommunicationError:
            return False
        except Pyro4.errors.PyroError:
            return False

    def __check_ping_is_success(self, service_name, response):
        if response != "ok":
            print(f'{service_name} tidak aktif :(')
            return False
        else:
            return True


def has_key(dictionary, key):
    if key in dictionary:
        return True
    else:
        return False
