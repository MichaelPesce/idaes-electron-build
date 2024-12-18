import sys
import os
import glob
import argparse

from pathlib import Path

## the entrypoints need to be stored in a package that will have a 'dist.info' folder in the final python executable
## currently, one of those is the python package wheel
## unknown why certain packages make it into the executable and others do not

ENTRYPOINTS_PACKAGE = "wheel"

def update_entry_points(project):

    ## temporarily use workarounds
    if project == "prommis":
        conda_package_name = "prommis"
        entry_points_project_name = "prommis"
    elif project == "idaes":
        conda_package_name = "idaes_pse"
        entry_points_project_name = "idaes"
    else:
        conda_package_name = project
        entry_points_project_name = project

    conda_prefix = os.environ["CONDA_PREFIX"]

    try:
        if sys.platform == "darwin":
            print("darwin")
            entrypoints_src_path = (
                f"{conda_prefix}/lib/python*/site-packages/{conda_package_name}-*info/entry_points.txt"
            )
            entrypoints_dst_path = f"{conda_prefix}/lib/python*/site-packages/{ENTRYPOINTS_PACKAGE}-*info/entry_points.txt"
        elif sys.platform == "linux":
            print("linux")
            entrypoints_src_path = (
                f"{conda_prefix}/lib/python*/site-packages/{conda_package_name}-*info/entry_points.txt"
            )
            entrypoints_dst_path = f"{conda_prefix}/lib/python*/site-packages/{ENTRYPOINTS_PACKAGE}-*info/entry_points.txt"
        else:
            # print("windows")
            entrypoints_src_path = (
                f"{conda_prefix}/lib/site-packages/{conda_package_name}-*info/entry_points.txt"
            )
            entrypoints_dst_path = (
                f"{conda_prefix}/lib/site-packages/{ENTRYPOINTS_PACKAGE}-*info/entry_points.txt"
            )
    except Exception as e:
        print(f"unable to get entry points src/dst: {e}")

    print(f"globbing from {entrypoints_src_path} to {entrypoints_dst_path}")

    entrypoints_src_glob = glob.glob(entrypoints_src_path)
    entrypoints_dst_glob = glob.glob(entrypoints_dst_path)

    print(f"entrypoints_src_glob: {entrypoints_src_glob}\nentrypoints_dst_glob: {entrypoints_dst_glob}")

    entrypoints_src = entrypoints_src_glob[0]
    entrypoints_dst = entrypoints_dst_glob[0]

    print(f"entrypoints_src: {entrypoints_src}\nentrypoints_dst: {entrypoints_dst}")

    entry_points = []
    start_getting_entries = False
    with open(entrypoints_src, "r") as f:
        for line in f:
            if f"[{entry_points_project_name}.flowsheets]" in line:
                start_getting_entries = True
            elif start_getting_entries == True and ("]" in line or line == None or line == "\n"):
                print(f"reached end of entry points, breaking")
                break
            elif start_getting_entries:
                entry = line.replace("\n", "")
                if line is not None:
                    entry_points.append(entry)
                else:
                    print(f"line is none, breaking")

    ## if entry points for this project exist, remove current set of entry points
    entrypoints_dst_str = ""
    found_entrypoints = False
    with open(entrypoints_dst, "r") as f:
        for line in f:
            if f"[{entry_points_project_name}.flowsheets]" in line:
                found_entrypoints = True
            elif found_entrypoints == True and (line == None or line == "\n"):
                found_entrypoints = False
            elif found_entrypoints:
                entry = line.replace("\n", "")
            else:
                entrypoints_dst_str+=line

    ## remove any trailing new lines
    while entrypoints_dst_str[-1] == "\n":
        entrypoints_dst_str = entrypoints_dst_str[0:-1]

    ## add in entrypoints from the list
    entrypoints_dst_str+=f"\n\n[{entry_points_project_name}.flowsheets]"
    for each in entry_points:
        entrypoints_dst_str+=f"\n{each}"

    ## write this string to the dst path
    with open(entrypoints_dst, "w") as f:
        f.write(entrypoints_dst_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", help="Project to search for entry points. If not provided, default is WaterTAP.")
    args = parser.parse_args()
    project = args.project
    if project is None:
        project = "watertap"
    elif project.lower() == "idaes":
        project = "idaes"
    else:
        project = project.lower()
    update_entry_points(project)
    