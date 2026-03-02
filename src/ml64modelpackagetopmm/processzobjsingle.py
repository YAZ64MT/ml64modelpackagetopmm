import sys
import argparse
from pathlib import Path
from typing import Sequence
from zipfile import is_zipfile
from ml64modelpackagetopmm.zobjprocessor import process_pak, process_zip


def _is_pakfile(pak: Path) -> bool:
    try:
        pakbytes = pak.read_bytes()
        pakbytes.index(b"ModLoader64")
        pakbytes.index(b"MLPublish.......")
        return True
    except:
        pass

    return False


def process_zobjs_single(output: Path, input: Path) -> None:
    if input.is_file():
        if is_zipfile(input):
            process_zip(output, input)
            return
        elif _is_pakfile(input):
            process_pak(output, input)
            return

    print(f"{input} is not a valid pak or zip!")


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="Extracts zobjs from a single ML64 .pak or .zip mod and embeds metadata for PlayerModelManager."
    )
    parser.add_argument("-o", "--output", help="Destination folder.", type=Path)
    parser.add_argument(
        "-i", "--input", help="zip or pak file containing ML64 model.", type=Path
    )
    args = parser.parse_args(argv)

    if type(args.output) is not Path or type(args.input) is not Path:
        parser.print_help()
    else:
        process_zobjs_single(args.output, args.input)

    return 0


if __name__ == "__main__":
    sys.exit(_main())
