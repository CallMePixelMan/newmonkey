import pathlib

from newmonkey.cli import setup_arg_parser
from newmonkey.parsing import get_discord_cache_directory, process_all_files


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()

    if args.discord_cache_dir is None:
        args.discord_cache_dir = get_discord_cache_directory()

        if args.discord_cache_dir is None:
            print("Your system is not supported. Please create an issue on GitHub.")
            return 1
        elif not args.discord_cache_dir.exists():
            print("Discord cache folder autodection was unsuccessful. Use the -d flag.")
            return 1

    print(f"Using discord cache folder {str(args.discord_cache_dir)!r}.")

    if args.out_dir is None:
        args.out_dir = pathlib.Path.cwd() / "newmonkey_output"
        args.out_dir.mkdir(exist_ok=True)
        print(f"Using output directory {str(args.out_dir)!r}.")

    process_all_files(
        args.discord_cache_dir,
        args.out_dir,
        args.cpu,
        args.all_files,
        args.stats,
        args.silent,
    )


if __name__ == "__main__":
    exit(main())
