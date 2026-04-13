"""
Intent labels — training examples live in ``training_corpus.py`` (large editable list).
"""

from typing import List, Tuple

INTENT_FILE_DELETE = "file_delete"
INTENT_FILE_COPY = "file_copy"
INTENT_FILE_MOVE = "file_move"
INTENT_FILE_LIST = "file_list"
INTENT_FILE_READ = "file_read"
INTENT_FILE_MKDIR = "file_mkdir"
INTENT_NAV_CD = "nav_cd"
INTENT_NAV_PWD = "nav_pwd"
INTENT_PROC_LIST = "proc_list"
INTENT_PROC_KILL = "proc_kill"
INTENT_SYSTEM_INFO = "system_info"
INTENT_SEARCH_GREP = "search_grep"
INTENT_FIND_FILES = "find_files"
INTENT_NET_PING = "net_ping"
INTENT_ENV_SHOW = "env_show"
INTENT_HELP = "help"
INTENT_UNKNOWN = "unknown"

ALL_INTENTS: List[str] = [
    INTENT_FILE_DELETE,
    INTENT_FILE_COPY,
    INTENT_FILE_MOVE,
    INTENT_FILE_LIST,
    INTENT_FILE_READ,
    INTENT_FILE_MKDIR,
    INTENT_NAV_CD,
    INTENT_NAV_PWD,
    INTENT_PROC_LIST,
    INTENT_PROC_KILL,
    INTENT_SYSTEM_INFO,
    INTENT_SEARCH_GREP,
    INTENT_FIND_FILES,
    INTENT_NET_PING,
    INTENT_ENV_SHOW,
    INTENT_HELP,
    INTENT_UNKNOWN,
]


def training_pairs() -> List[Tuple[str, str]]:
    """Build (text, label) pairs from the editable corpus."""
    from app.nlu.training_corpus import CORPUS

    pairs: List[Tuple[str, str]] = []
    for intent, utterances in CORPUS.items():
        for u in utterances:
            pairs.append((u.strip(), intent))
    return pairs
