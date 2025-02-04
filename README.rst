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

WIP

License
-------

``rgcompiler`` is licensed under the AGPL-3.0-or-later.
