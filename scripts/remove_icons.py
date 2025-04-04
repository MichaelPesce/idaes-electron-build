import os

def remove_ico_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".ico"):
            os.remove(os.path.join(directory, filename))
            print(f"Removed {filename}")

if __name__ == "__main__":
    directory = output_path="../electron/build"
    try:
        remove_ico_files(directory)
    except Exception as e:
        print(f"unable to remove icons: {e}")