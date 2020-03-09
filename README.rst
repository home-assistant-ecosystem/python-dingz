python-dingz
============

Python API for interacting with `Dingz <https://dingz.ch>`_ devices.

This module is not official, developed, supported or endorsed by iolo AG or
myStrom AG. For questions and other inquiries, use the issue tracker in this
repository please.

Without the support of iolo AG and myStrom AG it would have taken much longer
to create this module which is the base for the integration into
`Home Assistant <https://home-assistant.io>`_. Both companies have provided
and are still providing hardware, valuable feedback and advice. Their
continuous support make further development of this module possible.

See `api.dingz.ch <https://api.dingz.ch/>`_ for the API details.

Limitations
-----------

This module is at the moment limited to consuming sensor data, device details,
device configurations and states.
The front LED can be controlled but buttons requires you to programm them by
yourself.

No support for setting timers and schedules.

Requirements
------------

You need to have `Python 3 <https://www.python.org>`_ installed.

- `dingz <https://dingz.ch>`_ device
- Network connection
- Devices connected to your network

You need to know the IP address of the devices. Please consult your router
documentation to get this information.

Installation
------------

The package is available in the `Python Package Index <https://pypi.python.org/>`_ .

.. code:: bash

    $ pip install dingz

Usage
-----

Every unit has its own web interface: `http://IP_ADDRESS <http://IP_ADDRESS>`_

License
-------

``python-dingz`` is licensed under ASL 2.0, for more details check LICENSE.
