#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements a simple HTTP(S) proxy.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements a simple HTTP(S) proxy.
"""

__version__ = "0.0.2"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = "This package implements a simple HTTP(S) proxy."
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/SimpleHttpProxy"

copyright = """
SimpleHttpProxy  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["AbcHttpProxy"]

print(copyright)

from ssl import create_default_context, _create_unverified_context #, SSLContext, PROTOCOL_TLS_SERVER
from socketserver import BaseRequestHandler, ThreadingMixIn, TCPServer
from asyncio import run, create_task, open_connection
from argparse import Namespace, ArgumentParser
from socket import socket, create_connection
from sys import stdout, exit, _getframe
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from functools import partial
from binascii import hexlify
from string import printable
from typing import Union

printable: bytes = printable[:-5].encode('latin-1')

def clientTCP(ip: str, port: int, data: bytes, ssl: bool = False, onlysecure: bool = False) -> bytes:

    """
    This function implements a single request TCP client.
    """

    connection = socket()
    connection.connect((ip, port))

    if ssl:
        context = create_default_context() if onlysecure else _create_unverified_context()
        secure_connection = context.wrap_socket(connection)
    else:
        secure_connection = connection

    secure_connection.sendall(data)
    data = secure_connection.recv(65535)
    secure_connection.close()
    connection.close()
    return data

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass

class AbcHttpProxy(ABC):

    """
    This class implements a base for TCP proxy.
    """

    def __init__(self, interface: str = "0.0.0.0", port: int = 8012, onlysecure: bool = False): #, context: SSLContext = None):
        self.onlysecure = onlysecure
        self.interface = interface
        #self.context = context
        self.port = port

    @staticmethod
    @abstractmethod
    def handle_request(data: bytes) -> Union[bytes, None]:

        """
        This method should implements the special behaviour
        before sending client request to the server.
        """

        pass

    @staticmethod
    @abstractmethod
    def handle_response(data: bytes) -> Union[bytes, None]:

        """
        This method should implements the special behaviour
        before sending server response to the client.
        """

        pass

    def start(self) -> None:
        
        """
        This method start the proxy server.
        """
        
        onlysecure = self.onlysecure
        connect_response = b' 200 OK\r\n\r\n'

        class Server(BaseRequestHandler):
        
            """
            This class implements the server behaviour.
            """
            
            # context = self.context
            handle_request = self.handle_request
            handle_response = self.handle_response

            async def handle_CONNECT(self, host: bytes, request: bytes) -> None:
            
                """
                This function implements the CONNECT
                method requests and responses.
                """
                
                async def recv_send(reader, writer, handler) -> None:
                
                    """
                    Asynchronous coroutines to handle and send received data. 
                    """
                
                    data = 1
                    while data:
                        data = await reader(65535)
                        data = handler(data) or data
                        writer(data)

                connection = self.request
                client_reader, client_writer = await open_connection(sock=connection)

                ip, port = host.split(b':', 1)
                response = request.split(b'\r\n', 1)[0] + connect_response
                response = self.handle_response(response) or response
                connection.sendall(response)

                server_reader, server_writer = await open_connection(ip, port)

                client_recv = create_task(recv_send(client_reader.read, server_writer.write, self.handle_request))
                await recv_send(server_reader.read, client_writer.write, self.handle_response)
                await client_recv

                client_writer.close()
                server_writer.close()
                connection.close()
        
            def handle(self, ip: str = None, port: int = None, secure: bool = False) -> None:
            
                """
                This function implements receive
                and send requests and responses.
                """
            
                connection = self._request = self.request
                
                # if self.context:
                #    self.request = self.context.wrap_socket(connection, server_side=True)

                request = connection.recv(65535)
                request = self.handle_request(request) or request

                if not ip and not port:
                    method, url, request = request.split(b' ', 2)
                    
                    if method == b'CONNECT':
                        return run(self.handle_CONNECT(url, request))

                    parser = urlparse(url)
                    port = parser.port
                    ip = parser.hostname

                    full_path = (
                        parser.path + (b"" if parser.params == b"" else (b";" + parser.params))
                        + (b"" if parser.query == b"" else (b";" + parser.query))
                        + (b"" if parser.fragment == b"" else (b"#" + parser.fragment))
                    )

                    secure = parser.scheme == b"https"
                    if port is None:
                        port = 443 if secure else 80
                        
                    request = method + b' ' + full_path + b' ' + request

                response = clientTCP(ip, port, request, secure, onlysecure)
                response = self.handle_response(response) or response
                connection.sendall(response)

        with ThreadedTCPServer((self.interface, self.port), Server) as server:
            server.serve_forever()
            
class ProxyHttpPrinter(AbcHttpProxy):

    """
    This class implements a "Proxy Printer",
    to print requests and responses.
    """

    @staticmethod
    def hexareader(type_: str, data: bytes) -> bytes:

        """
        This function read data as hexadecimal reader.
        """
        
        to_print = type_ + "\n"
        counter = 0

        while data != b'':
            temp = data[:16]
            data = data[16:]
            to_print += (
                " \t" + hex(counter)[2:].ljust(4, "0") # hex(65535 // 16 + 1) == '0x1000'
                + " \t" + hexlify(temp, " ").decode('ascii').ljust(47)
                + " \t" + "".join(chr(char) if char in printable else "." for char in temp)
                + '\n'
            )
            counter += 1

        print(to_print)
        return data
    
    handle_request = partial(hexareader, "Request:")
    handle_response = partial(hexareader, "Response:")

def parse_args() -> Namespace:

    """
    This function parses the command line arguments.
    """
    
    parser = ArgumentParser(description=__description__)
    add_argument = parser.add_argument

    add_argument("-i", "--interface", default="", help="The interface to start the proxy server.")
    add_argument("-p", "--port", type=int, default=8012, help="The port to start the proxy server.")

    # add_argument("-K", "--private-key", help="The private key file path to load SSLContext.")
    # add_argument("-C", "--cert-chain", help="The cert chain file path to load SSLContext.")
    
    add_argument("-s", "--unsecure", default=True, action="store_false", help="Do not check SSL certificates (hostname and validity).")

    return parser.parse_args()

def main() -> int:

    """
    The main function to execute the file from the command line.
    """
    
    arguments = parse_args()
    _getframe(1).f_locals.update(arguments.__dict__)
    
    # context = None
    # if private_key and cert_chain:
        # context = SSLContext(PROTOCOL_TLS_SERVER)
        # context.load_cert_chain(cert_chain, private_key)

    proxy = ProxyHttpPrinter(interface, port, unsecure) #, context)
    
    try:
        print(f"Start server on tcp://{interface}:{port}...")
        proxy.start()
    except KeyboardInterrupt:
        print("Server down.")
        return 0


if __name__ == "__main__":
    exit(main())
