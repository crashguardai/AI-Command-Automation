"""
Large training set for intent classification.

Two parts:
1. **Template combinations** — many grammatical variants of the same basic commands.
2. **Anchor phrases** — edge cases, jargon, OS-specific wording.

Edit anchors or templates below, then restart the server to retrain the classifier.
"""

from __future__ import annotations

from typing import Iterable, List


def _uniq(phrases: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for p in phrases:
        t = " ".join(p.split()).strip()
        if len(t) < 2 or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def _merge(*groups: Iterable[str]) -> List[str]:
    acc: List[str] = []
    for g in groups:
        acc.extend(g)
    return _uniq(acc)


# --- file_list: list / dir / show contents ---
def _corpus_file_list() -> List[str]:
    v = [
        "list",
        "show",
        "display",
        "print",
        "get",
        "enumerate",
        "show me",
        "please list",
        "please show",
        "can you list",
        "can you show",
        "I want to list",
        "I need to see",
        "I want to see",
        "let me see",
        "gimme",
        "give me",
    ]
    n = [
        "all files",
        "all the files",
        "every file",
        "the files here",
        "files",
        "files here",
        "files in this folder",
        "files in the current directory",
        "files in this directory",
        "the current directory",
        "this folder",
        "this directory",
        "folder contents",
        "directory contents",
        "the contents here",
        "everything here",
        "everything in this folder",
        "items here",
        "stuff in this folder",
    ]
    gen = [f"{a} {b}" for a in v for b in n]
    questions = [
        "what files are here",
        "what files are in this folder",
        "what is in this folder",
        "what is in the current directory",
        "what's in this directory",
        "whats in this folder",
        "which files are here",
        "show me what is in this folder",
    ]
    short = [
        "ls",
        "ls .",
        "ls -la",
        "ls -l",
        "ls -a",
        "dir",
        "dir .",
        "list directory",
        "directory listing",
        "show listing",
        "browse this folder",
        "open folder view",
        "see files",
        "see all files",
        "view folder",
        "view directory",
        "show hidden files too",
        "include hidden files",
        "list non hidden files",
        "flat list of files",
        "recursive file list",
        "list files recursively",
        "tree view of files",
        "inventory of files",
    ]
    return _merge(gen, questions, short)


def _corpus_file_delete() -> List[str]:
    v = [
        "delete",
        "remove",
        "erase",
        "rm",
        "unlink",
        "trash",
        "get rid of",
        "please delete",
        "please remove",
        "I want to delete",
        "I need to remove",
        "can you delete",
        "delete the",
        "remove the",
        "permanently delete",
        "wipe",
        "discard",
    ]
    n = [
        "file notes.txt",
        "file test.txt",
        "file old.log",
        "file data.csv",
        "file config.json",
        "this file",
        "that file",
        "the log file",
        "the temp file",
        "files named temp",
        "backup.zip",
        "readme.txt",
        "file at path ./x.txt",
        "file on desktop",
        "file in downloads",
    ]
    gen = [f"{a} {b}" for a in v for b in n]
    extra = [
        "delete file notes.txt",
        "rm -f error.log",
        "rm config.yaml",
        "remove file backup.zip",
        "erase report.pdf",
        "unlink tmp.dat",
        "delete ./local.db",
        "remove ..\\bad.exe",
        "delete file C:\\temp\\x.txt",
        "force delete file y.txt",
        "delete without prompt",
        "send file to trash",
    ]
    return _merge(gen, extra)


def _corpus_file_copy() -> List[str]:
    v = [
        "copy",
        "cp",
        "duplicate",
        "clone",
        "make a copy of",
        "copy over",
        "please copy",
        "can you copy",
        "I want to copy",
    ]
    pairs = [
        ("a.txt", "b.txt"),
        ("src", "dest"),
        ("config.json", "config.bak"),
        ("readme.md", "readme.old"),
        ("file1", "file2"),
        ("input.csv", "output.csv"),
        ("app.py", "app_backup.py"),
        ("data.db", "data.backup"),
    ]
    gen = []
    for a, b in pairs:
        gen.extend(
            [
                f"copy {a} to {b}",
                f"cp {a} {b}",
                f"duplicate {a} as {b}",
                f"copy file {a} to {b}",
            ]
        )
    extra = [
        "copy notes to backup folder",
        "backup database.sqlite",
        "clone settings to settings.old",
        "make duplicate of package.json",
        "copy from src to dest",
        "xcopy style copy a to b",
    ]
    return _merge(gen, extra)


def _corpus_file_move() -> List[str]:
    gen = []
    for a, b in [
        ("old.txt", "new.txt"),
        ("a.py", "b.py"),
        ("data.csv", "archive/"),
        ("file", "subfolder/"),
        ("x", "y"),
    ]:
        gen.extend(
            [
                f"move {a} to {b}",
                f"mv {a} {b}",
                f"rename {a} to {b}",
                f"move file {a} into {b}",
            ]
        )
    extra = [
        "relocate report to reports",
        "put file into subfolder",
        "shift logs to old_logs",
        "move up one directory",
        "rename config to config.old",
        "change filename from a to b",
    ]
    return _merge(gen, extra)


def _corpus_file_read() -> List[str]:
    v = [
        "read file",
        "open file",
        "cat",
        "display file",
        "show contents of",
        "show content of",
        "print contents of",
        "view file",
        "dump file",
        "type file",
        "output file",
        "please read",
        "show me file",
        "I want to read",
    ]
    files = [
        "settings.ini",
        "log.txt",
        "README.md",
        "package.json",
        ".env",
        "config.yaml",
        "data.csv",
        "notes.txt",
    ]
    gen = [f"{a} {f}" for a in v for f in files]
    gen += [f"cat {f}" for f in files]
    gen += [f"type {f}" for f in files]
    extra = [
        "read the first 100 lines of app.log",
        "show me what's inside todo.txt",
        "display readme",
        "open env for viewing only",
        "print file to stdout",
    ]
    return _merge(gen, extra)


def _corpus_file_mkdir() -> List[str]:
    v = [
        "mkdir",
        "md",
        "make directory",
        "create directory",
        "create folder",
        "make folder",
        "add folder",
        "add directory",
        "please create folder",
        "I want a folder named",
    ]
    names = ["build", "dist", "tmp", "logs", "output", "data", "src", "test", "new_folder"]
    gen = [f"{x} {n}" for x in v for n in names]
    gen += [f"mkdir {n}" for n in names]
    gen += [f"create folder {n}" for n in names]
    gen += [f"make dir {n}" for n in names]
    extra = [
        "ensure directory exists build",
        "create nested path a/b/c",
        "mkdir -p parent/child",
        "create subfolder under src",
    ]
    return _merge(gen, extra)


def _corpus_nav_cd() -> List[str]:
    paths = [
        "home",
        "projects",
        "documents",
        "downloads",
        "/var/log",
        "D:/code",
        "..",
        "../..",
        "src",
        "backend",
        "~",
    ]
    v = [
        "cd",
        "chdir",
        "go to",
        "go into",
        "change directory to",
        "navigate to",
        "switch to",
        "jump to",
        "enter directory",
        "open folder",
    ]
    gen = [f"{x} {p}" for x in v for p in paths]
    gen += [f"cd {p}" for p in paths]
    gen += [f"cd into {p}" for p in paths]
    extra = [
        "go up one level",
        "cd ..",
        "move to parent directory",
        "step into src folder",
    ]
    return _merge(gen, extra)


def _corpus_nav_pwd() -> List[str]:
    base = [
        "pwd",
        "print working directory",
        "print wd",
        "where am I",
        "where am i",
        "current directory",
        "current path",
        "current folder",
        "show cwd",
        "show pwd",
        "what directory am I in",
        "what is my cwd",
        "present working directory",
        "which directory",
        "full path of cwd",
        "echo pwd",
        "get current path",
        "tell me the current directory",
        "need path of working folder",
        "display full path",
        "where is my terminal pointed",
    ]
    polite = [f"please {x}" for x in ("show pwd", "print working directory", "tell me cwd")]
    return _merge(base, polite)


def _corpus_proc_list() -> List[str]:
    return _uniq(
        [
            "ps",
            "ps aux",
            "ps -ef",
            "tasklist",
            "list processes",
            "list all processes",
            "show processes",
            "show running processes",
            "running processes",
            "what is running",
            "what programs are running",
            "active processes",
            "enumerate processes",
            "process table",
            "task manager list",
            "show tasks",
            "list tasks",
            "cpu processes",
            "background jobs list",
            "jobs running",
            "top processes",
            "system processes",
        ]
    )


def _corpus_proc_kill() -> List[str]:
    pids = ["1234", "4321", "8888", "999", "42", "1000"]
    names = ["notepad", "chrome", "firefox", "node", "python", "java", "docker"]
    gen: List[str] = []
    for p in pids:
        gen.extend(
            [
                f"kill process {p}",
                f"kill {p}",
                f"kill pid {p}",
                f"terminate pid {p}",
                f"end task {p}",
                f"stop process id {p}",
            ]
        )
    for n in names:
        gen.extend(
            [
                f"kill {n}",
                f"kill the {n} process",
                f"terminate process {n}",
                f"stop {n}",
                f"taskkill {n}",
                f"force quit {n}",
            ]
        )
    extra = [
        "force kill process",
        "sigkill process",
        "kill -9 1234",
        "taskkill by pid",
    ]
    return _merge(gen, extra)


def _corpus_system_info() -> List[str]:
    v = [
        "system information",
        "system info",
        "system stats",
        "hardware info",
        "os version",
        "operating system",
        "cpu information",
        "processor info",
        "memory usage",
        "ram usage",
        "how much memory",
        "free ram",
        "disk usage",
        "disk space",
        "free disk space",
        "how much disk",
        "df",
        "free",
        "uname",
        "uptime",
        "load average",
        "neofetch style info",
        "machine summary",
        "host info",
        "show cpu info",
        "show memory info",
        "kernel version",
        "windows version",
        "wmic cpu",
        "check disk space",
        "how full is the drive",
        "vmstat style summary",
        "lscpu equivalent",
        "system overview",
    ]
    prefixes = ["show", "get", "display", "I want", "please show"]
    tails = ["system info", "disk usage", "memory usage", "cpu usage"]
    gen = [f"{p} {t}" for p in prefixes for t in tails]
    return _merge(v, gen)


def _corpus_search_grep() -> List[str]:
    v = [
        "grep",
        "grep -r",
        "ripgrep",
        "rg",
        "search for text",
        "find string",
        "find pattern",
        "look for",
    ]
    tail = [
        "error in log.txt",
        "TODO in src",
        "import in *.py",
        "password in config",
        "foo in bar.txt",
        "ERROR in logs",
        "def main in app.py",
    ]
    gen = [f"{a} {t}" for a in v for t in tail]
    extra = [
        "grep error .",
        "search project for FIXME",
        "ripgrep across codebase",
        "find lines matching regex",
    ]
    return _merge(gen, extra)


def _corpus_find_files() -> List[str]:
    exts = ["pdf", "py", "js", "ts", "md", "txt", "log", "yaml", "yml", "json", "xml", "jpg", "png"]
    gen = [f"find all {e} files" for e in exts]
    gen += [f"locate *.{e}" for e in exts]
    gen += [f"find files named *.{e}" for e in exts]
    extra = [
        "find file named readme",
        "find readme",
        "locate *.log",
        "find . -name '*.txt'",
        "find under project",
        "search for files called test",
        "where are jpg files",
        "discover png images",
        "find files matching *.md",
        "glob search for yaml",
        "find recursively in .",
        "where is my config file",
        "search disk for file.exe",
    ]
    return _merge(gen, extra)


def _corpus_net_ping() -> List[str]:
    hosts = [
        "google.com",
        "8.8.8.8",
        "1.1.1.1",
        "localhost",
        "127.0.0.1",
        "github.com",
        "example.com",
        "cloudflare.com",
        "microsoft.com",
    ]
    gen = [f"ping {h}" for h in hosts]
    gen += [f"ping {h} please" for h in hosts]
    gen += [f"please ping {h}" for h in hosts[:5]]
    extra = [
        "check if host is reachable",
        "test connectivity to server",
        "icmp ping",
        "is site up",
        "network test ping",
        "check if dns resolves and ping",
    ]
    return _merge(gen, extra)


def _corpus_env_show() -> List[str]:
    vars_ = ["PATH", "HOME", "USER", "SHELL", "TEMP", "TMP", "LANG", "PWD"]
    gen = [f"echo ${v}" for v in vars_]
    gen += [f"what is {v}" for v in vars_]
    gen += [f"show {v}" for v in vars_]
    base = [
        "printenv",
        "env",
        "set",
        "environment variables",
        "show environment",
        "show env vars",
        "list env",
        "display PATH",
        "what is PATH",
        "echo PATH",
        "echo $HOME",
        "show all exported variables",
        "shell environment",
        "list all environment variables",
        "dump env to console",
        "show variables for this shell",
    ]
    return _merge(base, gen)


def _corpus_help() -> List[str]:
    return _uniq(
        [
            "help",
            "help me",
            "--help",
            "-h",
            "/?",
            "what can you do",
            "what do you support",
            "list capabilities",
            "how to use this",
            "usage",
            "instructions",
            "supported commands",
            "show help",
            "manual",
            "documentation",
            "explain yourself",
            "what are you for",
            "capabilities",
            "features",
        ]
    )


def _corpus_unknown() -> List[str]:
    return _uniq(
        [
            "order pizza",
            "hello",
            "how are you",
            "good morning",
            "tell me a joke",
            "weather today",
            "stock price",
            "translate to spanish",
            "write an essay",
            "email someone",
            "book a flight",
            "random words",
            "asdfasdf",
            "thanks",
            "bye",
            "lol",
            "this is frustrating",
            "not working",
            "why broken",
            "you suck",
            "meaning of life",
            "who won the superbowl",
            "recipe for cake",
            "call a taxi",
            "sing a song",
            "play music",
            "open youtube",
            "bitcoin price",
            "my horoscope",
            "debug my relationship",
            "quantum physics",
            "who is the president",
            "capital of france",
            "convert dollars to euros",
            "schedule meeting",
            "send sms",
            "buy crypto",
            "vpn recommendation",
        ]
    )


def _build_corpus() -> dict[str, list[str]]:
    return {
        "file_delete": _corpus_file_delete(),
        "file_copy": _corpus_file_copy(),
        "file_move": _corpus_file_move(),
        "file_list": _corpus_file_list(),
        "file_read": _corpus_file_read(),
        "file_mkdir": _corpus_file_mkdir(),
        "nav_cd": _corpus_nav_cd(),
        "nav_pwd": _corpus_nav_pwd(),
        "proc_list": _corpus_proc_list(),
        "proc_kill": _corpus_proc_kill(),
        "system_info": _corpus_system_info(),
        "search_grep": _corpus_search_grep(),
        "find_files": _corpus_find_files(),
        "net_ping": _corpus_net_ping(),
        "env_show": _corpus_env_show(),
        "help": _corpus_help(),
        "unknown": _corpus_unknown(),
    }


CORPUS: dict[str, list[str]] = _build_corpus()
