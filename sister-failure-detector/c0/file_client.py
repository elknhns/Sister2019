import Pyro4


def test_no_ns():
    uri = "PYRO:obj_27d7c59497c44c688319f7d8a4a95935@localhost:40549"
    file_server = Pyro4.Proxy(uri)
    # print(gserver.get_greet('ronaldo'))


def test_with_ns():
    uri = "PYRONAME:fileserver@localhost:7777"
    file_server = Pyro4.Proxy(uri)
    print(file_server)
    # response = __upload_file(file_server, "greet.py")
    response = file_server.get_all_files_name()
    # response = file_server.read_file_by_name("greet.py")
    # response = file_server.delete_file_by_name("greet.py")
    # response = file_server.update_file("greet.py", "Hello WOrld")
    print(response)


def __upload_file(file_server, file_path):
    with open(file_path, "r") as file:
        content = file.read()
        return file_server.upload_file(file.name, content)


if __name__ == '__main__':
    test_with_ns()
