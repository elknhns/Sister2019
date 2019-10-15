import random
import threading
import Pyro4
import time


@Pyro4.behavior(instance_mode="single")
class GreetServer(object):
    def __init__(self):
        # Centralized Heartbeat
        # threading.Thread(target=self.thread_send_heartbeat_to_central, kwargs={'interval_time': 1}).start()
        # All to All Heartbeat
        self.services = {}
        self.register_service("Failure Detector Service", "PYRONAME:failuredetectorserver@localhost:7777")
        self.register_service("File Service", "PYRONAME:fileserver@localhost:7777")
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
                    service_proxy.send_heartbeat("Greet Service", sequence_number)
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

    def send_heartbeat(self, service_name, sequence_number):
        self.current_services_heartbeat[service_name] = sequence_number

    def register_service(self, service_name, service_url):
        self.services[service_name] = service_url
        return self.services

    def thread_send_heartbeat_to_central(self, interval_time):
        uri = "PYRONAME:failuredetectorserver@localhost:7777"
        sequence_number = 0
        while True:
            sequence_number += 1
            failure_detector_server = Pyro4.Proxy(uri)
            try:
                failure_detector_server.send_heartbeat("greetserver", sequence_number)
            except Pyro4.errors.CommunicationError:
                print("Gagal mengirim heartbeat")
            except Pyro4.errors.PyroError:
                print("Gagal mengirim heartbeat")
            time.sleep(interval_time)


    def get_greet(self, name='NoName'):
        lucky_number = random.randint(1, 100000)
        return "Hello {}, this is your lucky number {}".format(name, lucky_number)


if __name__ == '__main__':
    k = GreetServer()
    print(k.get_greet('royyana'))
