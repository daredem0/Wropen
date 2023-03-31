#!/usr/bin/env python3
"""
TODO

:since: 26.03.2023
:author: Florian Leuze - f.leuze@outlook.de
:note: Encoding: UTF-8
"""

import os
import re
import sys
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen

import anybadge


OK_LINE = "would be reformatted"
NOK_LINE = "would be left unchanged"


def run_pylint(path: str, modules: list = []):
    """Run pylint on a list of python modules

    Args:
        path (str): root path
        modules (list, str): List of python modules. Defaults to [].

    Raises:
        FileNotFoundError: If list of modules is empty.
        FileNotFoundError: If a module cannot be found.

    Returns:
        float: Mean Score over all provided modules
    """
    c_dir = os.getcwd()
    os.chdir(path)
    path = os.path.abspath(path)
    if len(modules) == 0:
        raise FileNotFoundError("No modules provided.")
    score_list = []
    count = 0
    for count, mod in enumerate(modules):
        print(f"Linting {mod}")
        if not os.path.exists(os.path.abspath(mod)):
            raise FileNotFoundError(
                f"Module {mod} does not exist at {os.path.join(path, mod)}"
            )
        proc = Popen(
            [
                "python3",
                "-m",
                "pylint",
                "-r",
                "yes",
                "--rcfile",
                os.path.join(path, ".pylintrc"),
                os.path.join(path, mod),
            ],
            stdout=PIPE,
            stderr=PIPE,
        )  # , shell=True)
        out, _ = proc.communicate(timeout=100)
        os.chdir(c_dir)

        out_dec = out.decode("ascii")
        print(out_dec)
        lines = out_dec.splitlines()
        index = [
            idx
            for idx, substring in enumerate(lines)
            if "Your code has been rated" in substring
            and "substring" not in substring
        ][0]
        value = re.findall(r"\d+\.\d+", lines[index])[0]
        print(f"{mod} score: {value}")
        score_list.append(float(value))

    score = sum(score_list) / (count + 1)
    print("")
    print("Summary:")
    for mod, score in zip(modules, score_list):
        print(
            f"{mod.ljust(max((len(mod) for mod in modules)))} score: {score:5.2f}"
        )
    print(f"Score: {score}")
    return score


def create_badge(score: float = 0.00):
    """Create a gitlab badge containing lint score

    Args:
        score (float, optional): pylint score. Defaults to 0.00.
    """
    thresholds = {2: "red", 4: "orange", 6: "yellow", 10: "green"}
    os.mkdir("./pylint")
    badge = anybadge.Badge("pylint", score, thresholds=thresholds)
    badge.write_badge("pylint/pylint.svg")
    badge = anybadge.Badge("codestyle", "black", default_color="black")
    badge.write_badge("pylint/black.svg")


if __name__ == "__main__":
    DESCRIPTION = """
    Enforce codestyle or analyze for it
    Usage:
             python codestyle.py -p ./path                    # enforces style
             python codestyle.py -p ./path --dry (optional)   # checks for style
    """
    # pylint: disable=C0103
    ret_val = False
    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=DESCRIPTION, formatter_class=RawDescriptionHelpFormatter
        )
        codestyle = parser.add_argument_group("Check and enforce codestyle")
        lint = parser.add_argument_group("Use pylint")
        parser.add_argument(
            "-V", "--version", action="version", version="codestyle 00.00.01"
        )
        parser.add_argument(
            "-p",
            "--path",
            dest="path",
            action="store",
            default="./",
            help="Root path",
        )
        lint.add_argument(
            "-l",
            "--lint",
            dest="lint",
            action="store_true",
            default=False,
            help="Lint modules",
        )
        lint.add_argument(
            "-m",
            "--modules",
            dest="modules",
            action="store",
            nargs="+",
            default=[],
            help="Modules that shall be linted.",
        )
        lint.add_argument(
            "-t",
            "--target-score",
            dest="target_score",
            action="store",
            default=7.0,
            type=float,
            help="Define a target for the linter. Defualt: 7.0",
        )

        args, remaining_args = parser.parse_known_args()
        if len(remaining_args) > 0:
            print(f"trouble for remaining args: {remaining_args}")
            if not remaining_args[0].startswith("#"):
                raise ValueError("Illegal Parmaters")
        if "--help" not in args:
            if args.lint:
                r_score = run_pylint(args.path, args.modules)
                create_badge(r_score)
                ret_val = args.target_score < r_score
        else:
            parser.print_help(sys.stdout)
    except KeyboardInterrupt as _:
        sys.exit()
    except Exception as _err:
        print("Error: " + str(_err.args))
        raise _err
    sys.exit(not ret_val)
    # pylint: enable=C0103
