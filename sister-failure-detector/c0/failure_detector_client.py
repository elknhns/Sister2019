import Pyro4


def test_with_ns():
    uri = "PYRONAME:failuredetectorserver@localhost:7777"
    failure_detector_server = Pyro4.Proxy(uri)
    print(failure_detector_server)
    # response = failure_detector_server.ping_services()
    response = failure_detector_server.get_all_services_name()
    print(response)


if __name__ == '__main__':
    test_with_ns()
