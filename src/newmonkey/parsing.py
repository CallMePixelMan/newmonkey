import pathlib
import os
import time
import functools
import sys
from multiprocessing import Pool

import magic


END_SUFFIX = b"\x41\x0D\x97\x45\x6F\xFA\xF4\x01\x00\x00\x00"
START_SUFFIX = b"\x30\x5C\x72\xA7\x1B\x6D\xFB\xFC"


class InvalidCacheFileFormat(Exception):
    pass


def get_discord_cache_directory() -> pathlib.Path | None:
    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData" / "Roaming" / "discord" / "Cache"
    elif sys.platform == "linux":
        return home / ".config" / "discord" / "Cache" / "Cache_Data"
    elif sys.platform == "darwin":
        return home / "Library" / "Application Support" / "discord" / "Cache"
    else:
        return None


def parse_cache_file(cache_file_data: bytes) -> tuple[bytes, str, str | None, str]:
    """Parse a cache file as raw data.

    Args:
        cache_file_data (bytes): The data from a cache file.

    Raises:
        InvalidFormat: Cache data did not start with the expected start prefix.
        InvalidFormat: No source URL found.
        InvalidFormat: Data end suffix was not found.

    Returns:
        tuple[bytes, str, str | None, str]:
            The original file data, the domain that hosted the ressource,
            the kind of data if it comes from discord, and the mime type of the data.
    """
    # Discord has its own cache file type, stored as binary data.
    #
    # The first 8 bytes are always the same.
    #
    # There is an 32 bit integer from byte 12 to 15 that represents the length of the
    # origin source URL starting at byte 24.
    #
    # From then, the original file data is written until the following ending sequence:
    #   \x41\x0D\x97\x45\x6F\xFA\xF4\x01\x00\x00\x00
    #
    # Remaining fill data stores some miscellaneous metadata (for example, about
    # Cloudflare) and is not usefull in our case.

    if not cache_file_data.startswith(START_SUFFIX):
        raise InvalidCacheFileFormat(
            "Cache data did not start with expected start prefix."
        )

    # Parse the 32 bit integer offset and find the index of the first byte of the
    # original data.
    offset = int.from_bytes(cache_file_data[12:16], byteorder="little")
    data_start = 24 + offset

    # Extract the URL and the kind of data if it comes from discord.
    origin_url = cache_file_data[28:data_start].decode()
    if not origin_url:
        raise InvalidCacheFileFormat(f"{cache_file_data} does not contain any url.")
    _http, _empty, domain, datakind, *_leftover = origin_url.split("/", maxsplit=4)
    if "discord" not in domain or datakind == "api":
        datakind = None

    # Collect each byte until the end suffix is found.
    acc = list[int]()
    index = data_start
    end_suffix_found = False
    while index + len(END_SUFFIX) < len(cache_file_data) and not end_suffix_found:
        current_byte = cache_file_data[index]

        end_suffix_found = (
            cache_file_data[index : index + len(END_SUFFIX)] == END_SUFFIX
        )

        if not end_suffix_found:
            acc.append(current_byte)

        index += 1

    if not end_suffix_found:
        raise InvalidCacheFileFormat("End suffix was not found.")

    output = bytes(acc)
    return output, domain, datakind, magic.from_buffer(output, mime=True)


def open_and_parse_cache_file(
    cache_filepath: pathlib.Path,
) -> tuple[bytes, str, str | None, str]:
    """Same as parse_cache_file, but open the cac.

    Args:
        filepath (pathlib.Path): The cache file path.

    Returns:
        tuple[bytes, str, str | None, str]: Data returned from parse_cache_file.
    """
    with open(cache_filepath, "rb") as binfile:
        return parse_cache_file(binfile.read())


def create_file_from_cache_file(
    all_files: bool,
    root: pathlib.Path,
    cache_filepath: pathlib.Path,
) -> tuple[str | None, str | None]:
    try:
        raw_data, domain, kind, mime_type = open_and_parse_cache_file(cache_filepath)
    except InvalidCacheFileFormat:
        return None, None

    category, extension = mime_type.split("/")

    if category != "image" and not all_files:
        return None, None

    if kind is None:
        category_path = root / category / "other" / domain
    else:
        category_path = root / category / kind
    category_path.mkdir(parents=True, exist_ok=True)

    full_path = category_path / f"{cache_filepath.name}.{extension}"
    full_path.touch()
    full_path.write_bytes(raw_data)

    return domain, mime_type


def dict_increment(d: dict[str | None, int], key: str | None):
    if key not in d.keys():
        d[key] = 0
    d[key] += 1


def process_all_files(
    discord_cache_directory: pathlib.Path,
    dump_directory: pathlib.Path,
    cpu_core_to_use: int,
    all_files: bool,
    show_stats: bool,
    silent: bool,
):
    files = os.listdir(discord_cache_directory)
    files_count = len(files)

    to_cache_dump = functools.partial(
        create_file_from_cache_file, all_files, dump_directory
    )

    start_time = time.perf_counter()

    types = dict[str | None, int]()
    domains = dict[str | None, int]()
    sorted_count = 0
    with Pool(cpu_core_to_use) as pool:
        results = pool.imap_unordered(
            to_cache_dump,
            (
                filepath
                for filename in files
                if (filepath := discord_cache_directory / filename).is_file()
            ),
        )

        index = 0
        for index, (domain, mime_type) in enumerate(results):
            sorted_count += mime_type is not None

            if not silent:
                print(f"\rtotal:{index}/{files_count} sorted:{sorted_count}", end="")

            dict_increment(types, mime_type)
            dict_increment(domains, domain)

    end_time = time.perf_counter()

    if not silent:
        print()
        print("\nDone! ✨ 🍰 ✨")
        print(
            f"{files_count - sorted_count} items were not exported as there are not parsable, or not an image while --all-files was not used."  # noqa: E501
        )
        print(
            f"Ignored {files_count - index} items from cache folder that are not cached data."  # noqa: E501
        )
        print(f"Took {(end_time - start_time):.2f}s.")

        if show_stats:
            print("\nTYPES:")
            print("\n".join(f"{_type}: {count}" for _type, count in types.items()))
            print("\nDOMAINS:")
            print("\n".join(f"{domain}: {count}" for domain, count in domains.items()))
