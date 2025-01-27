![SimpleHttpProxy logo](https://mauricelambert.github.io/info/python/code/SimpleHttpProxy_small.png "SimpleHttpProxy logo")

# SimpleHttpProxy

## Description

This package implements a simple and partially asynchronous HTTP(S) proxy.

## Requirements

This package require:

 - python3
 - python3 Standard Library

## Installation

### Pip

```bash
python3 -m pip install SimpleHttpProxy
```

### Git

```bash
git clone "https://github.com/mauricelambert/SimpleHttpProxy.git"
cd "SimpleHttpProxy"
python3 -m pip install .
```

### Wget

```bash
wget https://github.com/mauricelambert/SimpleHttpProxy/archive/refs/heads/main.zip
unzip main.zip
cd SimpleHttpProxy-main
python3 -m pip install .
```

### cURL

```bash
curl -O https://github.com/mauricelambert/SimpleHttpProxy/archive/refs/heads/main.zip
unzip main.zip
cd SimpleHttpProxy-main
python3 -m pip install .
```

## Usages

### Default proxy printer using command line

```bash
python3 SimpleHttpProxy.py -h
python3 ProxyPrinter.pyz --help

ProxyPrinter --interface 0.0.0.0 --port 8012 --unsecure
ProxyPrinter -i 0.0.0.0 -p 8012 -s
```

### Custom proxy using Python

Proxy Server:

```python
from SimpleHttpProxy import AbcHttpProxy

class ProxyRestrict(AbcHttpProxy):
	def handle_request(self, data: bytes) -> bytes:
		if b'://www.ruby-lang.org' in data.split(b"\r\n", 1)[0]:
			return data.replace(b'www.ruby-lang.org', b'www.python.org', 2)
		return data
	def handle_response(self, data: bytes) -> bytes:
		return data.replace(b'www.ruby-lang.org', b'www.python.org')

proxy = ProxyRestrict()
proxy.start()
```

Python Client:

```python
from urllib.request import Request, urlopen
r = Request("http://ruby-lang.org/")
r.set_proxy('127.0.0.1:8012', 'http')
print(urlopen(r).read()[3150:4000].decode())
```

#### Screenshots

![Firefox proxy configuration](https://raw.githubusercontent.com/mauricelambert/SimpleHttpProxy/main/FirefoxConfig.PNG "Firefox proxy configuration")

![Default: Proxy Printer](https://raw.githubusercontent.com/mauricelambert/SimpleHttpProxy/main/ProxyPrinter.png "Default: Proxy Printer")

![Custom: Proxy Restriction](https://raw.githubusercontent.com/mauricelambert/SimpleHttpProxy/main/ProxyRestriction.png "Proxy Restriction")

## Links

 - [Pypi](https://pypi.org/project/SimpleHttpProxy/)
 - [Github](https://github.com/mauricelambert/SimpleHttpProxy/)
 - [Documentation](https://mauricelambert.github.io/info/python/code/SimpleHttpProxy.html)
 - [Executable](https://mauricelambert.github.io/info/python/code/ProxyPrinter.pyz)
 - [Python Windows executable](https://mauricelambert.github.io/info/python/code/ProxyPrinter.exe)

## Licence

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).

