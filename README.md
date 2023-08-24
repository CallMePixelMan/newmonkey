<p align="center">
    <img src="https://raw.githubusercontent.com/CallMePixelMan/newmonkey/main/meta/logo.png">
</p>

# NewMonkey
A CLI tool to convert your discord cache back to the original files.

This project was made to fix some problem I had with cachemonkey, I was looking for a CLI approach with the hability to export all the cache in one go.

## Installation
You can install newmonkey using `pipx` (or any alternative supporting the `[project.scripts]` directive from `pyproject.toml`) or with `pip`.
```
pipx install newmonkey
```

## Usage
You can use newmonkey directly to export your cache to a folder inside your current working directory.
```sh
newmonkey  # If you installed it with pipx
python -m newmonkey  # If you installed it with pip
```

Use the `-o` flag to specify an output directory and the `-d` flag to specify your discord cache directory if newmonkey can't autodetect it.

More flags are available. Use the `--help` flag to learn how to use other flags.

You can also import newmonkey to embed it inside your own software if you feel the need to.

## Licence
