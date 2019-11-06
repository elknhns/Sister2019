import Pyro4
import base64
import json
import sys

namainstance = sys.argv[1] if len(sys.argv) >= 2 else "fileserver"


def get_fileserver_object():
    uri = "PYRONAME:{}@localhost:7777".format(namainstance)
    fserver = Pyro4.Proxy(uri)
    return fserver


if __name__ == '__main__':
    f = get_fileserver_object()

    print('CREATE')
    print(f.create('asd.pptx'))
    print(f.create('coba.pdf'))
    print('\n')

    print('UPDATE')
    print(f.update('asd.pptx', content=open('slide2.pptx', 'rb+').read()))
    print(f.update('coba.pdf', content=open('slide1.pdf', 'rb+').read()))
    print('\n')

    print('READ')
    d = f.read('asd.pptx')
    open('asd-kembali.pptx', 'w+b').write(base64.b64decode(d['data']))

    k = f.read('coba.pdf')
    open('coba-kembali.pdf', 'w+b').write(base64.b64decode(k['data']))
    print('\n')

    print('LIST')
    print(f.list())
    print('\n')

    print('DELETE')
    print(f.delete('coba.pdf'))
    print('\n')