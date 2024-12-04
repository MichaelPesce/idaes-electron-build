# idaes-electron-builder

This repository is for building desktop versions of user interaces under the IDAES project.

## Getting started (developer)

### Prerequisites

The following steps assume that:

1. `conda` is already installed and configured
2. This repository (i.e. https://github.com/watertap-org/idaes-electron-build) has been cloned locally and the working directory is set to the root of the repository

## Setup

### 1. Creating the Conda environment

Run the following command to create and activate a new Conda environment named `flowsheet-processor-env`:

```sh
conda env create --file environment.yml && conda activate flowsheet-processor-env
```

This will install the correct runtime versions of both the backend (Python) and frontend (NodeJS) portions of the UI, as well as the backend (Python) dependencies.

### 2. Generate package.json

From the root directory, run the following python file:

```sh
python scripts/set_configuration.py -p <project-you-wish-to-build>
```

This will create a package.json file environment files that are required to create the Electron package. Project options are watertap, prommis, and idaes.

# Building production Electron app

The following steps assume that:

1. `conda` is already installed and configured
2. `flowsheet-processor-env` Conda environment is active

### 1. Transfer Entry points

```sh
cd <idaes-electron-build>
python scripts/move_entrypoints.py
```

### 2. Install IDAES Flowsheet Processor Locally

```console
cd <idaes-electron-build>/electron
git clone https://github.com/watertap-org/idaes-flowsheet-processor-ui.git && cd idaes-flowsheet-processor-ui && pip install --progress-bar off .
```

### 3. Install proper project (IDAES, WaterTAP, or PROMMIS)

```console
pip install <project>
```

### 4. Create build distribution

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