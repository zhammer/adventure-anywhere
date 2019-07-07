import re
import textwrap


def _notice(notice_text: str) -> str:
    return textwrap.fill(notice_text)


line_delimiter = "			      - - -"

help_and_info_prefix_notice = _notice(
    '(SOME OF THE ORIGINAL ADVENTURE COMMANDS LIKE "HELP" AND "INFO" '
    "ARE INTERCEPTED BY THE SMS TEXT MESSAGE PROVIDER BEFORE THEY CAN "
    'BE PROCESSED BY THE GAME. IF YOU RUN INTO THIS ISSUE, TYPE "GAME " '
    'BEFORE THE COMMAND, SUCH AS "GAME HELP" OR "GAME INFO".)'
)

restart_notice = _notice('(TYPE "RESTART" TO RESTART THE GAME.)')


def add_after_start_message(start_text: str) -> str:
    return "\n".join(
        [
            start_text.rstrip("\n"),
            line_delimiter,
            help_and_info_prefix_notice,
            line_delimiter,
            restart_notice,
        ]
    )


def strip_sms_bypass_prefix(command_text: str) -> str:
    """
    >>> strip_sms_bypass_prefix("game help")
    'help'
    >>> strip_sms_bypass_prefix("take lamp")
    'take lamp'
    >>> strip_sms_bypass_prefix("east")
    'east'
    """
    return re.sub(r"^game ", "", command_text)


def is_restart_command(command_text: str) -> bool:
    """
    >>> is_restart_command("restart")
    True
    >>> is_restart_command("restart game")
    True
    >>> is_restart_command("take lamp")
    False
    """
    return command_text.startswith("restart")
