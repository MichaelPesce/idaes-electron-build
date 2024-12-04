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
python scripts/generate_json.py -p <project-you-wish-to-build>
```

This create a package.json file that will be used to create the Electron package. Project options are watertap, prommis, and idaes.

# Building production Electron app

The following steps assume that:

1. `conda` is already installed and configured
2. The WaterTAP-UI package has been succesfully installed
3. Watertap is cloned and installed locally. This is required for transferring data files (png and yaml)
4. Watertap and Watertap-ui directories must be inside of the same parent directory. 
5. `watertap-ui-env` Conda environment is active

### 1. Transfer Entry points

```sh
cd <watertap-ui-path>/electron
npm --prefix electron run move-entrypoints
```

### 2. Create build distribution

### Windows:
#### Requirements: 
1) Windows operating system
2) The following environment variables must be set
    - CSC_LINK: "<path-to-valid-codesigning-certificate.p12>"
    - CSC_KEY_PASSWORD: "<codesign-account-password>"

#### Command:
```console
cd <watertap-ui-path>/electron
npm run dist:win
```

### Mac (requires Mac OS):
#### Requirements: 
1) Mac operationg system
2) Signed in to Apple developer account
3) A valid <u>Developer ID Application</u> certificate AND corresponding private key stored in keychain access

#### Command:

```console
cd <watertap-ui-path>/electron
npm run dist:mac
```