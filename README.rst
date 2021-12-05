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
documentation to get this information or use the `dingz` CLI tool.

Installation
------------

The package is available in the `Python Package Index <https://pypi.python.org/>`_ .

.. code:: bash

    $ pip install dingz

On a Fedora-based system or on a CentOS/RHEL machine which has EPEL enabled.

.. code:: bash

    $ sudo dnf -y install python3-dingz

For Nix or NixOS users is a package available. Keep in mind that the lastest releases might only
be present in the ``unstable`` channel.

.. code:: bash

    $ nix-env -iA nixos.python3Packages.dingz

Module usage
------------

Every unit has its own web interface: `http://IP_ADDRESS <http://IP_ADDRESS>`_ .

See `example.py` for detail about module.


How to operate shades / dimmers
-------------------------------

.. code:: python

    d = Dingz("ip_address_or_host")
    # Fetch config, this has to be done once to fetch all details about the shades/dimmers
    await d.get_devices_config()

    # Fetch the current state of the lights/vers
    await d.get_state()

    # Get details about shade
    shade_0 = d.shades.get(0)
    print("Blinds: %s Lamella: %s" % (shade_0.current_blind_level(), shade_0.current_lamella_level()))

    # Operate shade
    shade_0.shade_down()

    # Turn on light
    d.dimmers.get(2).turn_on(brightness_pct=70)


CLI usage
---------

The package contains a command-line tool which support some basic tasks.

.. code:: bash

   $ dingz discover


License
-------

``python-dingz`` is licensed under ASL 2.0, for more details check LICENSE.
