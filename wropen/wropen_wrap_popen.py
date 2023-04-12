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

import json
import subprocess
from enum import Enum
from functools import wraps
from io import StringIO
from typing import Any


class WropenMode(Enum):
    """Wropen mode enum."""

    PASS = 0x00
    """Sets Wropen to PASS mode (prints to stdout)."""
    FAIL = 0x01
    """Sets Wropen to FAIL mode (prints to stderr)."""


class WropenState:  # pylint: disable=R0903,R0913
    """Defines the persistent state of all Wropen instances."""

    def __init__(
        self,
        mode: WropenMode,
        path: str,
        path_err: str = None,
        debug: bool = False,
        encoding: str = None,
    ) -> None:
        """Construct the global Wropen instance.

        :param mode: Defines the current mode of the wropen instance.
        :type mode: WropenMode

        :param path: Json file containing the message definitions Wropen shall use.
        :type path: str

        :param path_err: Json file containing the message definitions for error mode. Default: None
        :type path_err: str

        :param debug: Activates subprocess.Popen interception. Default: True
        :type debug: bool

        :param encoding: If not None sets encoding for out/err. Default: None
        :type encoding: str
        """
        self.mode: WropenMode = mode
        self.debug: bool = debug
        self._path: str = path
        self._err_path: str = path_err
        self.encoding: str = encoding
        self.config_path: str = self._get_wropen_config_path()

    def _get_wropen_config_path(self) -> str:
        """Choose the appropriate wropen config path depending on the mode.

        :return: Path
        :rtype: str
        """
        if self.mode == WropenMode.PASS:
            return self._path
        return self._err_path


class WropenNotConfigured(Exception):
    """Raised when wropen state is unconfigured."""


class Wropen(subprocess.Popen):
    """Wropen Popen intercepter class."""

    state: WropenState = None

    def __init__(self, args, bufsize=-1, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=True,
                 shell=False, cwd=None, env=None, universal_newlines=None,
                 startupinfo=None, creationflags=0,
                 restore_signals=True, start_new_session=False,
                 pass_fds=(), *, user=None, group=None, extra_groups=None,
                 encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
        """Create new Popen instance."""
        self.stdout = StringIO()
        self.stdin = StringIO()
        self.stderr = StringIO()
        self.args = args
        self.stdin.write(" ".join(self.args))
        self.mode = WropenMode.PASS
        self.returncode = 0
        self._wropen_config = None
        self.init()
        self._init_stdout_stderr()

    def _init_stdout_stderr(self):
        (_stdout, _stderr) = self._get_reply()
        if self.state.encoding is not None:
            _stdout = _stdout.decode(encoding=self.state.encoding)
            _stderr = _stderr.decode(encoding=self.state.encoding)
        self.stdout.write(_stdout)
        self.stdout.seek(0)
        self.stderr.write(_stderr)
        self.stderr.seek(0)

    @staticmethod
    def intercept_popen(func):
        """Can be used as decorator wo intercept popen calls.

        :param func: The function that is decorated.
        :type func: Any
        """

        @wraps(func)
        def inner(*args, **kwargs):
            """Intercepts Wropen into the popen call."""
            if Wropen.state is None or not Wropen.state.debug:
                #print("Wropen inactive")
                return func(*args, **kwargs)
            _real_popen = getattr(subprocess, "Popen")
            try:
                # print("Intercepted popen execution.")
                setattr(
                    subprocess,
                    "Popen",
                    lambda *args, **kwargs: Wropen(*args, **kwargs),
                )
                return func(*args, **kwargs)
            finally:
                setattr(subprocess, "Popen", _real_popen)
                #print("Restore popen.")

        return inner

    @staticmethod
    def configure(state: WropenState) -> None:
        """Configure the Wropen object.

        :param state: Defines the inner state of Wropen.
        :type state: WropenState
        """
        Wropen.state = state

    def _load_config_as_json(self) -> Any:
        with open(self.state.config_path, "r", encoding="utf-8") as _wropen:
            _wropen_json = json.load(_wropen)
        return _wropen_json

    def init(self):
        """Initialize the Wropen object if it has been configured properly.
        All provided config files are loaded.

        :raises WropenNotConfigured: If Wropen object is not configured.
        """
        if self.state is None:
            raise WropenNotConfigured("You need to call Wropen.configure once.")
        self._wropen_config = self._load_config_as_json()

    def _init_streams(self):
        """Initialize stdin and stderr by piping stdint to stdout.

        :return: stdout, stdin
        :rtype: bytes, bytes
        """
        return self._encode(
            self.stdin.getvalue().encode("utf-8")
        ), self._encode(self.stderr.getvalue().encode("utf-8"))

    def _encode(self, message: str) -> Any:
        """Encode depending on the inner state of Wropen.

        :param message: The message that shall be printed.
        :type message: str

        :return: Bytes if encoding set, else str
        :rtype: Any
        """
        if self.state.encoding is not None:
            return message.encode(self.state.encoding)
        return message

    def _evaluate_args(self):
        """Depending on the type of the provided command concatenate
        it or pass it through directly.

        :return: Command
        :rtype: str
        """
        if isinstance(self.args, list):
            return " ".join(self.args)
        return self.args

    def _access_message(self, message: str, key: str) -> Any:
        _lines = self._wropen_config.get(message, {}).get(key, [])
        if len(_lines) <= 0:
            _lines = ""
        return self._encode("\n".join(_lines))

    def _access_return_code(self, message: str) -> Any:
        return self._wropen_config.get(message, {}).get("returncode", 0)

    def _search_for_stdin_in_config(self):
        for message_no in self._wropen_config:
            if (
                self._evaluate_args()
                == self._wropen_config[message_no]["message"]
            ):
                _stdout = self._access_message(message_no, "reply")
                _stderr = self._access_message(message_no, "error")
                self.returncode = self._access_return_code(message_no)
                return _stdout, _stderr
        return None

    def _get_reply(self):
        """Check if the message is defined in the provided json and get the reply.
        If no message is defined the stdin is piped into stdout.

        :return: stdout, stderr.
        :rtype: bytes, bytes
        """
        if (popen_result := self._search_for_stdin_in_config()) is not None:
            return popen_result
        return self._init_streams()

    def communicate(self, *args, **kwargs):  # pylint: disable=W0613
        """Immitate the communicate method and respond with stderr and stdour
        utf-8 encoded byte objects.

        :return: stdout, stderr.
        :rtype: bytes, bytes
        """
        return self._get_reply()
