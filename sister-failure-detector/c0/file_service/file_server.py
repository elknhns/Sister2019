from c0.file_service.file import *
import Pyro4


def start_without_ns():
    daemon = Pyro4.Daemon()
    x_file_server = Pyro4.expose(FileServer)
    uri = daemon.register(x_file_server)
    print("my URI : ", uri)
    daemon.requestLoop()


def start_with_ns():
    #name server harus di start dulu dengan  pyro4-ns -n localhost -p 7777
    #gunakan URI untuk referensi name server yang akan digunakan
    #untuk mengecek service apa yang ada di ns, gunakan pyro4-nsc -n localhost -p 7777 list
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost",7777)
    file_server = Pyro4.expose(FileServer)
    file_server_uri = daemon.register(file_server)
    print("URI file server : ", file_server_uri)
    ns.register("fileserver", file_server_uri)
    daemon.requestLoop()


if __name__ == '__main__':
    start_with_ns()
