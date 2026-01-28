from os import makedirs, walk
from pathlib import Path
from typing import Any
from ml64pypak.pakformat import Pak
from shutil import rmtree
import json
import tempfile
import zipfile


def copy_bytes(dest: bytearray, src: bytes, dest_index: int, count: int | None = None):
    if count is None:
        count = len(src)

    for i in range(count):
        dest[dest_index + i] = src[i]


def find_file_in_dir(to_find: str, dir: Path) -> Path | None:
    for root, dirnames, filenames in walk(dir):
        if to_find in filenames:
            return Path(root, to_find)

    return None


def handle_model(
    filename: str, display_name: str, out_dir: Path, root: Path, author=""
):
    try:
        zobj_path = Path(root, filename)

        if zobj_path.is_file():
            zobj = bytearray(zobj_path.read_bytes())

            if (
                zobj[0x5000 : 0x5000 + len(b"MODLOADER64")] == b"MODLOADER64"
                and zobj.find(b"PLAYERMODELINFO") < 0
                and len(zobj) > 0x5800
            ):
                header_location = 0x5500
                internal_name_field_size = 64
                display_name_field_size = 32
                author_name_field_size = 64

                internal_name_location = header_location + 0x10
                display_name_location = (
                    internal_name_location + internal_name_field_size
                )
                author_name_location = display_name_location + display_name_field_size

                relative_zobj_path = zobj_path.relative_to(root.parent)
                internal_name = str(relative_zobj_path).replace("\\", "/")

                internal_name_buf = bytes(internal_name, "utf-8")
                while len(internal_name_buf) > author_name_field_size - 1:
                    internal_name = internal_name[1:]
                    internal_name_buf = bytes(internal_name, "utf-8")

                copy_bytes(zobj, b"PLAYERMODELINFO", header_location)
                zobj[header_location + len(b"PLAYERMODELINFO")] = 1

                copy_bytes(zobj, internal_name_buf, internal_name_location)
                zobj[internal_name_location + len(internal_name_buf)] = 0

                display_name_buf = bytes(display_name, "utf-8")

                while len(display_name_buf) > internal_name_field_size:
                    display_name = display_name[:-1]
                    display_name_buf = bytes(display_name, "utf-8")

                copy_bytes(
                    zobj,
                    display_name_buf,
                    display_name_location,
                )

                if len(display_name_buf) < internal_name_field_size:
                    zobj[display_name_location + len(display_name_buf)] = 0

                author_buf = bytes(author, "utf-8")
                copy_bytes(
                    zobj,
                    author_buf,
                    author_name_location,
                )
                zobj[author_name_location + len(author_buf)] = 0

                dest = Path(out_dir, relative_zobj_path)

                makedirs(dest.parent, exist_ok=True)

                try:
                    dest.write_bytes(zobj)
                except:
                    print(f"Failed to write to {str(dest)}")
    except:
        pass


def handle_models(out_dir: Path, root: Path, model_info_list: list, author=""):
    if len(author) > 63:
        author = author[:63]

    for model_info in model_info_list:
        try:
            handle_model(
                model_info["file"],
                model_info["name"],
                out_dir,
                root,
                author,
            )
        except:
            pass


def process_ml64_model_package(output_dir: Path, input_dir: Path) -> None:
    package_json_path = find_file_in_dir("package.json", input_dir)

    if package_json_path is None:
        print(f"Could not find package.json in {input_dir}")
        return

    package: Any = None
    try:
        package = json.loads(package_json_path.read_text())
    except:
        print(f"Found package.json was not a valid json file!")

    author: str

    try:
        author = package["author"]
    except:
        author = ""

    root = package_json_path.parent

    try:
        handle_model(
            package["zzplayas"]["OcarinaOfTime"]["adult_model"],
            package["name"],
            output_dir,
            root,
            author,
        )
    except:
        pass

    try:
        handle_model(
            package["zzplayas"]["OcarinaOfTime"]["child_model"],
            package["name"],
            output_dir,
            root,
            author,
        )
    except:
        pass

    try:
        handle_model(
            package["zzplayas"]["MajorasMask"]["adult_model"],
            package["name"],
            output_dir,
            root,
            author,
        )
    except:
        pass

    try:
        handle_model(
            package["zzplayas"]["MajorasMask"]["child_model"],
            package["name"],
            output_dir,
            root,
            author,
        )
    except:
        pass

    try:
        handle_models(
            output_dir, root, package["zzplayas"]["OOT"]["adult_model"], author
        )
    except:
        pass

    try:
        handle_models(
            output_dir, root, package["zzplayas"]["OOT"]["child_model"], author
        )
    except:
        pass

    tunics = [
        ["kokiri", "(K. Tunic)"],
        ["goron", "(G. Tunic)"],
        ["zora", "(Z. Tunic)"],
    ]

    for tunic in tunics:
        try:
            handle_model(
                package["zzplayas"]["OOT"]["tunic_models_adult"][tunic[0]],
                package["name"] + f" {tunic[1]}",
                output_dir,
                root,
                author,
            )
        except:
            pass

        try:
            handle_model(
                package["zzplayas"]["OOT"]["tunic_models_child"][tunic[0]],
                package["name"] + f" {tunic[1]}",
                output_dir,
                root,
                author,
            )
        except:
            pass

    for i in range(20, 101, 20):
        try:
            handle_model(
                package["zzplayas"]["OOT"]["damage"][str(i)],
                package["name"] + f" ({i}%)",
                output_dir,
                root,
                author,
            )
        except:
            pass

    try:
        handle_models(
            output_dir, root, package["zzplayas"]["MM"]["adult_model"], author
        )
    except:
        pass

    try:
        handle_models(
            output_dir, root, package["zzplayas"]["MM"]["child_model"], author
        )
    except:
        pass


def process_pak(output_dir: Path, pak_path: Path, create_output_dir=False) -> None:
    if create_output_dir:
        output_dir = Path(output_dir, pak_path.stem)

    extracted_pkg = Path(tempfile.gettempdir(), "ml64playermodels", pak_path.stem)

    makedirs(extracted_pkg, exist_ok=True)

    Pak(str(pak_path)).extract_all(str(extracted_pkg))

    process_ml64_model_package(output_dir, extracted_pkg)

    rmtree(extracted_pkg)


def process_paks_in_dir(output_dir: Path, input_dir: Path) -> None:
    pak_files: list[Path] = []

    for root, dirnames, filenames in walk(input_dir):
        for filename in filenames:
            p = Path(root, filename)

            if p.suffix == ".pak":
                pak_files.append(p)

    for pak_file in pak_files:
        process_pak(output_dir, pak_file, True)


def process_zip(output_dir: Path, zip_path: Path, create_output_dir=False) -> None:
    if create_output_dir:
        output_dir = Path(output_dir, zip_path.stem)

    extracted_pkg = Path(tempfile.gettempdir(), "ml64playermodels", zip_path.stem)

    makedirs(extracted_pkg, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path) as zip_file:
            zip_file.extractall(extracted_pkg)
            process_ml64_model_package(output_dir, extracted_pkg)
            zip_file.close()
    except:
        pass

    rmtree(extracted_pkg, True)


def process_zips_in_dir(output_dir: Path, input_dir: Path):
    zip_files: list[Path] = []

    for root, dirnames, filenames in walk(input_dir):
        for filename in filenames:
            p = Path(root, filename)

            if p.suffix == ".zip":
                zip_files.append(p)

    for zip_file in zip_files:
        process_zip(output_dir, zip_file, True)
