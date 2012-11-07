"""Communication components

This package contains various components to deal with various means
of communication to the outside world.

* Functions     - communication related miscellaneous functions
* I2C           - i2c bus related components
* JSONServer    - a simple json server and helper components
* Maestro       - Pololu Maestro component
* Ping          - Active part of the ping system
* Pong          - reactive part of the ping system
"""

__all__ = ['Echo',
           'JSONServer',
           'Maestro',
           'Ping',
           'Pong',
           'WSGIGateway',
           'SerialPort',
]
