![SimpleHttpProxy logo](https://mauricelambert.github.io/info/python/code/SimpleHttpProxy_small.png "SimpleHttpProxy logo")

# SimpleHttpProxy

## Description

This package implements a simple and partially asynchronous HTTP(S) proxy.

## Requirements

This package require:

 - python3
 - python3 Standard Library

## Installation

```bash
pip install SimpleHttpProxy
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

```python
from SimpleHttpProxy import AbcHttpProxy

class ProxyRestrict(AbcHttpProxy):
	@staticmethod
	def handle_request(data: bytes) -> bytes:
		if b'://www.ruby-lang.org' in data.split(b"\r\n", 1)[0]:
			return data.replace(b'www.ruby-lang.org', b'www.python.org', 2)
		return data
	@staticmethod
	def handle_response(data: bytes) -> bytes:
		return data.replace(b'www.ruby-lang.org', b'python.org')
```

#### Screenshot

![Firefox proxy configuration](https://raw.githubusercontent.com/mauricelambert/SimpleHttpProxy/main/FirefoxConfig.PNG "Firefox proxy configuration")

![Default: Proxy Printer](https://raw.githubusercontent.com/mauricelambert/SimpleHttpProxy/main/ProxyPrinter.png "Default: Proxy Printer")

![Custom: Proxy Restriction](https://raw.githubusercontent.com/mauricelambert/SimpleHttpProxy/main/ProxyRestriction.png "Proxy Restriction")

## Links

 - [Github Page](https://github.com/mauricelambert/SimpleHttpProxy/)
 - [Pypi package](https://pypi.org/project/SimpleHttpProxy/)
 - [Documentation](https://mauricelambert.github.io/info/python/code/SimpleHttpProxy.html)
 - [Python Executable](https://mauricelambert.github.io/info/python/code/SimpleHttpProxy.pyz)

## Licence

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).

