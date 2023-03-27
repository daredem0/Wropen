#!/usr/bin/env python3
"""
TODO

Date: 26.03.2023
Author: Florian Leuze
E-Mail: f.leuze@outlook.de
Encoding: UTF-8

Copyright (c) 2023 Florian Leuze
"""
import json
import subprocess
from functools import wraps
from enum import Enum
from io import StringIO
from typing import Any


class WropenMode(Enum):
    """Wropen mode enum."""

    PASS = 0x00
    FAIL = 0x01


class WropenState:
    """Defines the persistent state of all Wropen instances."""

    def __init__(self, mode: WropenMode, path: str, path_err: str = None, debug: bool = False) -> None:
        self.mode: WropenMode = mode
        self.debug: bool = debug
        self._path: str = path
        self._err_path: str = path_err
        self.config_path: str = self._get_wropen_config_path()

    def _get_wropen_config_path(self) -> str:
        """Choose the appropriate wropen config path depending on the mode.

        Returns:
            str: path
        """
        if self.mode == WropenMode.PASS:
            return self._path
        return self._err_path


class WropenNotConfigured(Exception):
    """Raised when wropen state is unconfigured."""


class Wropen(subprocess.Popen):
    """Wropen Popen intercepter class."""

    state: WropenState = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stdout = StringIO()
        self.stdin = StringIO()
        self.stderr = StringIO()
        self.mode = WropenMode.PASS
        self.returncode = 0
        self._wropen_config = None
        self.init()

    @staticmethod
    def intercept_popen(func):
        """Can be used as decorator wo intercept popen calls.

        Args:
            func (Any): The function that is decorated.
        """
        @wraps(func)
        def inner() -> None:
            """Intercepts Wropen into the popen call."""
            if not Wropen.state.debug:
                func()
                return
            _real_popen = getattr(subprocess, "Popen")
            try:
                print("Intercepted popen execution.")
                setattr(subprocess, "Popen", lambda *args, **kwargs: Wropen(*args, **kwargs))
                func()
            finally:
                setattr(subprocess, "Popen", _real_popen)
                print("Restore popen.")

        return inner

    @staticmethod
    def configure(state: WropenState) -> None:
        """Configure the Wropen object.

        Args:
            state (WropenState): Defines the inner state of Wropen.
        """
        Wropen.state = state

    def _load_config_as_json(self) -> Any:
        """Load json config file.

        Returns:
            dict: json dump
        """
        with open(self.state.config_path, "r", encoding="utf-8") as _wropen:
            _wropen_json = json.load(_wropen)
        return _wropen_json

    def init(self):
        """Initialize the Wropen object if it has been configured properly.
        All provided config files are loaded.

        Raises:
            WropenNotConfigured: If Wropen object is not configured.
        """
        if self.state is None:
            raise WropenNotConfigured("You need to call Wropen.configure once.")
        self._wropen_config = self._load_config_as_json()

    def _init_streams(self):
        """Initialize stdin and stderr by piping stdint to stdout.

        Returns:
            bytes, bytes: stdout, stdin
        """
        return self.stdin.getvalue(), self.stderr.getvalue()

    def _get_reply(self):
        """Check if the message is defined in the provided json and get the reply.
        If no message is defined the stdin is piped into stdout.

        Returns:
            bytes, bytes: stdout, stderr
        """
        for message_no in self._wropen_config:
            if " ".join(self.args) == self._wropen_config[message_no]["message"]:
                _stdout = self._wropen_config.get(message_no, {}).get("reply", "").encode("utf-8")
                _stderr = self._wropen_config.get(message_no, {}).get("error", "").encode("utf-8")
                return _stdout, _stderr
        return self._init_streams()

    def communicate(self):
        """Immitate the communicate method and respond with stderr and stdour
        utf-8 encoded byte objects.

        Returns:
            bytes, bytes: stdout, stderr
        """
        return self._get_reply()
