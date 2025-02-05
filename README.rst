rgcompiler
==========

``rgcompiler`` is a project for manipulating RPG Maker XP files with a focus on the fangame
Pokémon Reborn.

``rgcompiler`` has two components; the compiler + decompiler itself, and ``rhodochrosite``: a
Ruby marshaller and unmarshaller that supports the latest version of the Ruby marshal format.

Notes
-----

- All data read and saved by ``rgcompiler`` is in *little endian* format. The official RGSS uses
  machine endian, but in practice nearly all of these files are built and written on x86_64 machines
  so it is worth explicitly defining them to be little endian.

- ``rhodochrosite`` will produce larger files than ``Marshal.dump`` as it does not support writing
  object links. Object links are a weird feature of the marshal format that is awkward to support in
  Python due lists and dicts being unhashable, as well as if the VM considers two objects to be
  the same being an implementation detail.

  The size difference is especially notable on marshal files with large numbers of floats or
  strings, which are normally deduplicated by ``Marshal.dump``.

  ``rhodochrosite`` *does* support loading object links written from ``Marshal.dump`` correctly
  because links are identified by-id and it is simple to save every object seen.

Usage
-----

``rgcompiler`` currently contains a set of debugging commands used to test and develop the internal
functionality of the project.

- ``rgd-ruby-unmarshal``: Unmarshal a Ruby marshal file to JSON. This was used to figure out the
  format of the RPG Maker event files; these JSON files do not contain enough information to be
  re-marshaled.

- ``rgd-ruby-roundtrip``: Round-trips a Ruby marshal file. This loads a Ruby marshal file then
  immediately re-saves it. This was used to test the correctness of ``rhodochrosite``, and to verify
  that ``mkxp-z`` and the editor could read the round-tripped files.

- ``rgd-verify-maps``: Verifies that ``rgcompiler`` can read all possible maps from a project. This
  was used to easily isolate and implement unknown commands and is not useful anymore; it is kept
  around for potentially enabling ``rgcompiler`` to work with newer RPG Maker games.

Tests
-----

``rgcompiler`` has a test suite that can be ran with ``pytest``. It is recommended to run this
with ``-n <THREADS> --dist worksteal`` as the roundtrip tests are expensive and embarassingly
arallel.

License
-------

``rgcompiler`` is licensed under the AGPL-3.0-or-later.
