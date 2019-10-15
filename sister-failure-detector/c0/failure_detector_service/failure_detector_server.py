from c0.failure_detector_service.failure_detector import *
import Pyro4
import threading


def start_with_ns():
    # name server harus di start dulu dengan  pyro4-ns -n localhost -p 7777
    # gunakan URI untuk referensi name server yang akan digunakan
    # untuk mengecek service apa yang ada di ns, gunakan pyro4-nsc -n localhost -p 7777 list
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 7777)
    failure_detector_server = Pyro4.expose(FailureDetectorServer)
    failure_detector_server_uri = daemon.register(failure_detector_server)
    print("URI failure detector server : ", failure_detector_server_uri)
    ns.register("failuredetectorserver", failure_detector_server_uri)
    daemon.requestLoop()


if __name__ == '__main__':
    start_with_ns()
