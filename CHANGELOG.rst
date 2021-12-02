Changelog
=========

0.5.0 (2021-12-02)
------------------

- Rename module from python-dingz to dingz

0.4.0 (2021-12-02)
------------------

- Support for dimmers
- Allos later async_timeout
- Refactored shades

  - With version 0.3.0
    ::

          dingz.shade_down(shade_id)

  - Starting from 0.4.0:
    ::

          shade = dingz.shades.get(shade_id)
          shade.shade_down()


0.3.0 (2020-11-08)
------------------

- Add CLI tool
- Support for shades/blinds (@retoo)
- Access to more parts of the dingz API (blind config, system config and others) (@retoo)
- Automatic discovery for dingz units in the local network (@retoo)

0.2.0 (2020-05-20)
------------------

- First public release (Hardware is available)


0.1.0 (2020-03-09)
------------------

- Feature complete for basic handling

0.0.1 (2019-12-27)
------------------

- Initial release
