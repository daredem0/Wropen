#!/usr/bin/env python3
"""
Wropen is a module that allows a minimalistic and almost non intrusive way
of intercepting subprocess.Popen calls for unit testing. It mostly aims to
provide a simple way of adding unit tests to legacy code without digging
to deep, as a refactoring can be done better after unit testing is added.


:since: 26.03.2023
:author: Florian Leuze - f.leuze@outlook.de
:note: Encoding: UTF-8
"""
from .wropen_wrap_popen import Wropen
from .wropen_wrap_popen import WropenMode
from .wropen_wrap_popen import WropenNotConfigured
from .wropen_wrap_popen import WropenState
