coeasm
=======

.. image:: https://img.shields.io/pypi/v/coegen.svg
    :target: https://pypi.python.org/pypi/coegen

A tiny assembler for a processor that's being implemented in VHDL
I should probably host the VHDL source on git somehwere... and then merge this INTO it... because otherwise... it doesn't make sense

Installing coeasm
==================

Install from pip::

    pip3 install coeasm

For development, clone from github and run the tests with::

    git clone https://github.com/CptSpaceToaster/coeasm.git
    cd coeasm
    make test

Usage
=====

Help::

    coeasm -h

TODO
====
I need to check that the @[number] generates a warning or error if the user jumps to a section in memory that already contains instructions.

There is no check for instructions that currently need an address like LOAD, versus instructions that don't, like LSL.  Currently, if you specify an address after LSL, it will write it to memory, generating a buggy coefile.  
