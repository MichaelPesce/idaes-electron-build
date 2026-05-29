import importlib
from pathlib import Path
import re
import os
from dotenv import load_dotenv

load_dotenv()

imports = set()
datas = []

project = os.getenv("project")
additional_modules = os.getenv("additional_modules", None)
print(f"project is {project}")
default_packages = ["pyomo", "scipy"]
if additional_modules is not None:
    if "," in additional_modules:
        additional_modules_list = additional_modules.split(",")
    else:
        additional_modules_list = [additional_modules]
    default_packages.extend(additional_modules_list)
default_packages.append(project)
packages = default_packages
print("packages to scan:", packages)
for package in packages:
    pkg = importlib.import_module(package)
    try:
        # base_folder = Path(pkg.__path__[0])
        pkg_path = Path(pkg.__file__).parent
        base_folder = pkg_path.parent
        print("------------------importing", package, base_folder, pkg_path)
    except TypeError:  # missing __init__.py perhaps
        print(
            f"---------------Cannot find package '{package}' directory, possibly "
            f"missing an '__init__.py' file"
        )
    if not pkg_path.is_dir():
        print(
            f"--------------------Cannot load from package '{package}': "
            f"path '{pkg_path}' not a directory"
        )

    skip_expr = re.compile(r"_test|test_|__")
    print("beginning python files")
    for python_file in pkg_path.glob("**/*.py"):
        if skip_expr.search(str(python_file)):
            continue
        # print(python_file)
        relative_path = python_file.relative_to(pkg_path)
        dotted_name = relative_path.as_posix()[:-3].replace("/", ".")
        module_name = package + "." + dotted_name
        try:
            module = importlib.import_module(module_name)
            imports.add(module_name)
            # print(module_name)
        except Exception as err:  # assume the import could do bad things
            print(f"Import of file '{python_file}' failed: {err}")
            continue

        # ensure all parent modules are imported (a lot of repeats here but it works)
        relative_path = relative_path.parent
        while relative_path != Path("."):
            dotted_name = relative_path.as_posix().replace("/", ".")
            module_name = package + "." + dotted_name
            try:
                module = importlib.import_module(module_name)
                imports.add(module_name)
                relative_path = relative_path.parent
            except:
                relative_path = relative_path.parent
                print("error on my part")
                continue

    # add all png files to pyinstaller data
    for png_file in pkg_path.glob("**/*.png"):
        file_name = "/" + png_file.as_posix().split("/")[-1]
        # print(file_name)
        if skip_expr.search(str(png_file)):
            continue
        relative_path = png_file.relative_to(pkg_path)
        dotted_name = relative_path.as_posix()
        src_name = f"{base_folder}/" + package + "/" + dotted_name
        dst_name = package + "/" + dotted_name.replace(file_name, "")
        try:
            datas.append((src_name, dst_name))
        except Exception as err:  # assume the import could do bad things
            print(f"Import of file '{png_file}' failed: {err}")
            continue

    # add all json files to pyinstaller data
    for json_file in pkg_path.glob("**/*.json"):
        file_name = "/" + json_file.as_posix().split("/")[-1]
        # print(file_name)
        if skip_expr.search(str(json_file)):
            continue
        relative_path = json_file.relative_to(pkg_path)
        dotted_name = relative_path.as_posix()
        src_name = f"{base_folder}/" + package + "/" + dotted_name
        dst_name = package + "/" + dotted_name.replace(file_name, "")
        try:
            datas.append((src_name, dst_name))
        except Exception as err:  # assume the import could do bad things
            print(f"Import of file '{json_file}' failed: {err}")
            continue

    # track traversed directories
    # we need to maintain the entire directory structure inside the pyinstaller build,
    # to ensure that all imports in the python code work.
    traversed_dirs = set()
    
    # add all yaml files to pyinstaller data
    for yaml_file in pkg_path.glob("**/*.yaml"):
        file_name = "/" + yaml_file.as_posix().split("/")[-1]
        if skip_expr.search(str(yaml_file)):
            continue
        relative_path = yaml_file.relative_to(pkg_path)
        dotted_name = relative_path.as_posix()
        src_name = f"{base_folder}/" + package + "/" + dotted_name
        dst_name = package + "/" + dotted_name.replace(file_name, "")
        try:
            datas.append((src_name, dst_name))
            # Record all ancestor dirs of this yaml file
            for parent in relative_path.parents:
                if parent != Path("."):
                    traversed_dirs.add(parent)
        except Exception as err:
            print(f"Import of file '{yaml_file}' failed: {err}")
            continue

    # Also walk ALL subdirectories, not just those containing yaml files
    for sub_dir in pkg_path.glob("**/"):
        rel = sub_dir.relative_to(pkg_path)
        if rel != Path(".") and not skip_expr.search(str(sub_dir)):
            traversed_dirs.add(rel)

    # For each traversed directory, ensure PyInstaller creates it by
    # dropping a sentinel .keep file if no yaml was already added there
    dirs_with_data = {Path(dst.replace(package + "/", "", 1)) for _, dst in datas}
    for dir_path in traversed_dirs:
        if dir_path not in dirs_with_data:
            sentinel_src = pkg_path / dir_path / ".keep"
            sentinel_src.touch(exist_ok=True)  # create empty sentinel on disk
            dst_name = package + "/" + dir_path.as_posix()
            datas.append((str(sentinel_src), dst_name))
            print(f"Added sentinel for empty dir: {dst_name}")

hiddenimports = list(imports)
# add lorem ipsum.txt for jaraco
datas.append(("./Lorem ipsum.txt", "jaraco/text"))
if project == "watertap":
    datas.append((src_name, "watertap/core"))
hiddenimports.append("jaraco.text")

pyomo_imports = [
    "networkx",
    "pint",
    "numbers",
    "pyutilib",
    "sys",
    "logging",
    "re",
    "pkg_resources.extern",
    "pyomo.common.dependencies.numpy",
    "collections.abc",
    "types",
    "pyutilib",
    "pyutilib.component",
    "importlib.abc",
    "importlib",
    "ctypes",
    "random",
    "yaml",
    "numpy",
    "scipy._lib.array_api_compat.numpy.fft",
    "scipy._lib.array_api_compat.numpy",
    "scipy._lib.array_api_compat",
    "scipy._lib.",
    "scipy.sparse",
    "scipy.special._special_ufuncs",
    "scipy.special._cdflib",
    "scipy.special",
]

hiddenimports.extend(pyomo_imports)

print(f"datas: \n{datas}")
print(f"hiddenimports: \n{hiddenimports}")