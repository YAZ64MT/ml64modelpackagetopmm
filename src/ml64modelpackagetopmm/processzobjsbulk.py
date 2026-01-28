import sys
import argparse
from pathlib import Path
from ml64modelpackagetopmm.zobjprocessor import process_paks_in_dir, process_zips_in_dir

def process_zobjs_bulk(output: Path, input: Path) -> None:
    process_paks_in_dir(output, input)
    process_zips_in_dir(output, input)

def main(argv=sys.argv) -> int:
    parser = argparse.ArgumentParser(
        prog="Extracts zobjs from ML64 .pak and .zip mods and embeds metadata for PlayerModelManager."
    )
    parser.add_argument("-o", "--output", help="Destination folder.", type=Path)
    parser.add_argument(
        "-i", "--input", help="Folder containing .pak files and .zip files.", type=Path
    )
    args = parser.parse_args(argv)
    process_zobjs_bulk(args.output, args.input)
    return 0

if __name__ == "__main__":
    sys.exit(main())
