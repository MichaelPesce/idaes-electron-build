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

### 2. Install IDAES Flowsheet Processor Locally and run NPM install

```console
cd <idaes-electron-build>/electron
git clone https://github.com/prommis/idaes-flowsheet-processor-ui.git && cd idaes-flowsheet-processor-ui && pip install --progress-bar off .
```

### 3. Install proper project (IDAES, WaterTAP, or PROMMIS)

```console
pip install <project>
```

### 3.b Install supported versions of Numpy and Scipy
Not all versions of Numpy and Scipy will work with pyinstaller, and thus we some time have to specify a unique version. The compatibility will be a function of   operating system, version of watertap and pyinstaller, in many cases this might not be required. To check, look in .github\workflows\electron-build.yaml file to see if 
we are using any specific versions of Numpy or Scipy during electron-build workflow. As of writing this guide we use numpy 2.2.6, and scipy 1.15.3 with WaterTAP 1.14.0:

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
if your project requries additional modules, that are not part of standard watertap/promiss/idaes then add them via am option 
```sh
cd <idaes-electron-build>
python scripts/set_configuration.py -p <project-you-wish-to-build> -am <comma separated list of additonal modules> 
```

example (not, do not include spaces unless they are part of package name!)
```sh
cd <idaes-electron-build>
python scripts/set_configuration.py -p watertap -am my_custom_package_1,my_custom_package_2
```

### 6. Transfer Entry points

```sh
cd <idaes-electron-build>
python scripts/move_entrypoints.py
```

### 5 Install NPM
We should already be in flowsheet processor dir, so first install frontend NPM and then go and install main electron npm

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
