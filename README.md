# idaes-electron-builder

This repository is for building desktop versions of user interaces under the IDAES project. It is designed to create deployments in a GitHub workflow.

## Running a deployment dispatch

### Prerequisites

The following steps assume that:

1. `gh` is already installed and configured For installation instructions, see https://github.com/cli/cli.
2. This repository (i.e. https://github.com/prommis/idaes-electron-build) has been cloned locally and the working directory is set to the root of the repository

### Run application dispatch for WaterTAP

```sh
gh workflow run .github/workflows/build-dispatch.yml -f project=watertap -f os-version=windows-latest -f artifact-name=WaterTAP-Flowsheet-Processor -f pip-install-target=watertap@git+https://github.com/watertap-org/watertap@main
```

### Run application dispatch for IDAES

```sh
gh workflow run .github/workflows/build-dispatch.yml -f project=idaes -f os-version=windows-latest -f artifact-name=IDAES-Flowsheet-Processor -f pip-install-target=idaes-pse@git+https://github.com/IDAES/idaes-pse
```

### Run application dispatch for PROMMIS

```sh
gh workflow run .github/workflows/build-dispatch.yml -f project=prommis -f os-version=windows-latest -f artifact-name=PROMMIS-Flowsheet-Processor -f pip-install-target=prommis@git+https://github.com/prommis/prommis@main
```

These commands will initiate a windows deployment. For mac, use os-version=macos-latest. For a complete set of input options, see below:
- project
  - type: choice
  - options:
    - watertap
    - prommis
    - idaes
  - description: project name
- os-version
  - type: choice
  - options:
    - windows-latest
    - macos-latest
  - description: operating system
- pip-install-target
  - type: string
  - default: watertap@git+https://github.com/watertap-org/watertap@main
  - description: pip target for python project
- artifact-name
  - type: string
  - default: WaterTAP-Flowsheet-Processor
  - description: Build artifact name
- idaes-flowsheet-processor-ui-repo
  - type: string
  - default: prommis/idaes-flowsheet-processor-ui
  - description: IDAES Flowsheet Processor UI repository URL. Can be replaced by forks such as {github-user}/idaes-flowsheet-processor-ui
- idaes-flowsheet-processor-ui-ref
  - type: string
  - default: main
  - description: Branch or tag for IDAES Flowsheet Processor UI repository
- package-build-number
  - type: string
  - description: package build number

## Deploying local applications

### Prerequisites

The following steps assume that:

1. `conda` is already installed and configured
2. This repository (i.e. https://github.com/prommis/idaes-electron-build) has been cloned locally and the working directory is set to the root of the repository

## Setup

### 1. Creating the Conda environment

Run the following command to create and activate a new Conda environment named `ifp-build-env`:

```sh
conda env create --file environment.yml && conda activate ifp-build-env
```

This will install the correct runtime versions of both the backend (Python) and frontend (NodeJS) portions of the UI, as well as the backend (Python) dependencies.

### 2. Install IDAES Flowsheet Processor Locally

```console
cd <idaes-electron-build>/electron
git clone https://github.com/prommis/idaes-flowsheet-processor-ui.git && cd idaes-flowsheet-processor-ui && pip install --progress-bar off .
```

### 3.a Install proper project (IDAES, WaterTAP, or PROMMIS)

```console
pip install <project>
```

### 3.b Install any additional packages (Optional)
Install any other required packages via pip now. 

### 3.c Install supported versions of Numpy and Scipy (Optional)
Not all versions of Numpy and Scipy will work with pyinstaller, and thus we some time have to specify a unique version. The compatibility will be a function of operating system, version of watertap and pyinstaller, in many cases this might not be required. To check, look in .github\workflows\electron-build.yaml file to see if 
we are using any specific versions of Numpy or Scipy during electron-build workflow. The writer of this guide foudn he had to use numpy 2.2.6, and scipy 1.15.3 with WaterTAP 1.15dev0:

```consol
pip install numpy==2.2.6
pip install scipy==1.15.3
```


### 4. Generate package.json

From the root directory, run the following python file:

```sh
cd <idaes-electron-build>
python scripts/set_configuration.py -p <project-you-wish-to-build>
```
if your project requires additional modules, that are not part of standard watertap/promiss/idaes then add them via -am option 

```sh
cd <idaes-electron-build>
python scripts/set_configuration.py -p <project-you-wish-to-build> -am <comma separated list of additonal modules> 
```

example (note, do not include spaces unless they are part of package name!)\

```sh
cd <idaes-electron-build>
python scripts/set_configuration.py -p watertap -am my_custom_package_1,my_custom_package_2
```

### 5. Transfer Entry points

If your primary project has your entery points arleady defined that this command will work by default, just specify the project (default is WaterTAP)
```sh
cd <idaes-electron-build>
python scripts/move_entrypoints.py -p watertap
```

Otherwise you can provide entery points to add to existing, or to replace existing useing -ue command and -oe to specify if you want to overwite (True) or append (False, default)
```sh
cd <idaes-electron-build>
python scripts/move_entrypoints.py -p watertap -ue "custom_flowsheet = custom_module.flowsheets.costom_flowsheet.ui" 
```

This will replace default watertap flowsheets uis with your custom flowsheet
```sh
cd <idaes-electron-build>
python scripts/move_entrypoints.py -p watertap -ue "custom_flowsheet = custom_module.flowsheets.costom_flowsheet.ui" -oe True 
```

To specify more then one flowsheet, simply provide a comma deliminated list (e.g.)
```sh
cd <idaes-electron-build>
python scripts/move_entrypoints.py -p watertap -ue "custom_flowsheet_a = custom_module.flowsheets.costom_flowsheet_a_._ui,custom_flowsheet_b = custom_module.flowsheets.costom_flowsheet_b_ui" -oe True 
```

### 6. Install NPM
Install NPM for build and front end:
```console
cd <idaes-electron-build>/electron
npm install
cd <idaes-electron-build>/electron/idaes-flowsheet-processor-ui/frontend
npm clean-install
```

### 7. Create build distribution

### Windows:
#### Requirements: 
1) Windows operating system

#### Command:
```console
cd <idaes-electron-build>/electron
npm run dist:win
```

### Mac (requires Mac OS):
#### Requirements: 
1) Mac operationg system
2) Signed in to Apple developer account
3) A valid <u>Developer ID Application</u> certificate AND corresponding private key stored in keychain access

#### Command:

```console
cd <idaes-electron-build>/electron
npm run dist:mac
```

### 8. Testing your build
The build will be located inside the <idaes-electron-build>/electron/dist

In the folder there will be an installer file, and a folder with 'upacked' install.

### 8.1 Testing backend build on windows 

The most common issue with doing a new custom build is failure to include all packages or build the backend, one can test if the backend is build correctly and also get a clear trace error by finding the py_dist folder in electron. 
Go to:
``` 
<idaes-electron-build>/electron/py_dist/main
```

In there you will find a main.exe, execute inside a CMD so you can capture any errors:
```consol
main.exe
```

If all things are good it should show that your backend is loading and you should see that the application is started up, final messages should be something like this.
```
INFO:     Started server process [48008]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 8.2 Common issue with Numpy

On some systems, numpy might not properly be built and a different version might be needed. Refer to step 3.b, in this case you will see following error:

```
D:\github\idaes-electron-build\electron\py_dist\main>main.exe
PyInstaller\loader\pyimod02_importers.py:419: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.
Traceback (most recent call last):
  File "idaes_flowsheet_processor_ui\main.py", line 18, in <module>
  File "PyInstaller\loader\pyimod02_importers.py", line 419, in exec_module
  File "idaes_flowsheet_processor_ui\routers\flowsheets.py", line 16, in <module>
  File "PyInstaller\loader\pyimod02_importers.py", line 419, in exec_module
  File "pandas\__init__.py", line 31, in <module>
ImportError: Unable to import required dependencies:
numpy: Error importing numpy: you should not try to import numpy from
        its source directory; please exit the numpy source tree, and relaunch
        your python interpreter from there.
[47492] Failed to execute script 'main' due to unhandled exception!
```