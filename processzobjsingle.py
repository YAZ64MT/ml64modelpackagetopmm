import sys
import argparse
from pathlib import Path
from zipfile import is_zipfile
from zobjprocessor import process_pak, process_zip

def is_pakfile(pak: Path) -> bool:
    try:
        pakbytes = pak.read_bytes()
        pakbytes.index(b"Modloader64")
        pakbytes.index(b"MLPublish.......")
        return True
    except:
        pass

    return False

def process_zobjs_single(output: Path, input: Path) -> None:
    if is_zipfile(input):
        process_zip(output, input)
    elif is_pakfile(input):
        process_pak(output, input)
    else:
        print(f"{input} is not a valid pak or zip!")

def main(args=sys.argv) -> int:
    parser = argparse.ArgumentParser(
        prog="Extracts zobjs from ML64 .pak and .zip mods and embeds metadata for PlayerModelManager."
    )
    parser.add_argument("-o", "--output", help="Destination folder.", type=Path)
    parser.add_argument(
        "-i", "--input", help="zip or pak file containing ML64 model.", type=Path
    )
    args = parser.parse_args(args)
    
    process_zobjs_single(args.output, args.input)

    return 0

if __name__ == "__main__":
    sys.exit(main())
