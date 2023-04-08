#!/usr/bin/env python3
"""
TODO

Date: 26.03.2023
Author: Florian Leuze
E-Mail: f.leuze@outlook.de
Encoding: UTF-8

Copyright (c) 2023 Florian Leuze
"""

import os
import subprocess
import sys
from subprocess import PIPE
from typing import Callable


sys.path.append(os.path.dirname(os.getcwd()))
from wropen import Wropen
from wropen import WropenMode
from wropen import WropenState


DEBUG = False
WROPEN_PASS_PATH = "./wropen.json"
WROPEN_FAIL_PATH = "./wropen_fail.json"


@Wropen.intercept_popen
def run_test() -> None:
    with subprocess.Popen(
        ["ls", "-lh"], stdout=PIPE, stdin=PIPE, stderr=PIPE
    ) as proc:
        print_communicate(proc.communicate)


def print_communicate(func: Callable) -> None:
    out, err = func()
    print(out.decode("utf-8"), err.decode("utf-8"))


if __name__ == "__main__":
    wropen_state = WropenState(
        WropenMode.PASS, WROPEN_PASS_PATH, encoding="utf-8"
    )
    wropen_state.debug = False
    Wropen.configure(wropen_state)
    run_test()
    wropen_state.debug = True
    run_test()
    wropen_state.debug = False
    run_test()
