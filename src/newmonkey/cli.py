import argparse
import pathlib
import multiprocessing


def setup_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("newmonkey")
    parser.add_argument(
        "-o",
        "--out-dir",
        metavar="OUTPUT_DIRECTORY",
        help="Cache export directory. Will create a new directory if not specified.",
        type=pathlib.Path,
        default=None,
    )
    parser.add_argument(
        "-d",
        "--discord-cache-dir",
        metavar="DISCORD_CACHE_DIRECTORY",
        type=pathlib.Path,
        help="Discord cache directory. Will try to find it for you if not specified.",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--cpu",
        metavar="CPU_CORE_COUNT",
        help=(
            "The number of CPU core to use to parse cached files."
            "Will use all available ones by default."
        ),
        type=int,
        default=multiprocessing.cpu_count(),
    )
    parser.add_argument(
        "-a",
        "--all-files",
        action="store_true",
        help=(
            "Will export all files."
            "Turned off by default as a lot of files that are not images are unusable."
        ),
        default=False,
    )
    parser.add_argument(
        "-S",
        "--silent",
        action="store_true",
        help="Hide the progress counter and the stats.",
        default=False,
    )
    parser.add_argument(
        "-s",
        "--stats",
        action="store_true",
        help="Display stats about the exported files.",
        default=False,
    )

    return parser
