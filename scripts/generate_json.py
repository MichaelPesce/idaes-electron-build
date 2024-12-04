from datetime import datetime
import argparse
import json


JSON_FRAMEWORK = {
  "name": "idaes-flowsheet-processor-ui",
  "private": True,
  "main": "main.js",
  "dependencies": {
    "@electron/remote": "^2.0.8",
    "@emotion/react": "^11.11.4",
    "axios": "^0.27.2",
    "dotenv": "^16.0.1",
    "electron-is-dev": "^2.0.0",
    "electron-log": "^4.4.8",
    "electron-store": "^8.1.0"
  },
  "devDependencies": {
    "electron": "^20.1.3",
    "electron-builder": "^23.3.3",
    "electron-notarize": "^1.2.1"
  },
  "scripts": {
    "move-frontend-build-win": "move /Y ui/build build",
    "build-backend": "cd ../backend/app && pyinstaller -y --clean --distpath ../../electron/py_dist main.spec",
    "build-replace-backend": "npm run remove-previous-backend-build && npm run build-backend || npm run build-backend",
    "build-replace-backend-win": "npm run remove-previous-backend-build-win && npm run build-backend || npm run build-backend",
    "electron-build-mac": "npm run remove-previous-dist && electron-builder -m || electron-builder -m",
    "electron-build-win": "npm run remove-previous-dist-win && electron-builder -w || electron-builder -w",
    "dist:mac": "npm run build-replace-backend && npm run build-frontend && npm run electron-build-mac",
    "dist:win": "npm run build-replace-backend-win && npm run build-frontend-win && npm run electron-build-win",
    "dist:lin": "npm run build-replace-backend && npm run build-frontend && npm run electron-build-lin",
    "remove-previous-backend-build": "rm -r py_dist/*",
    "remove-previous-backend-build-win": "rd /S /Q py_dist",
    "remove-previous-dist": "rm -r dist/*",
    "remove-previous-dist-win": "rd /S /Q dist",
    "get-extensions-installer": "cd ../backend/app && pyinstaller -y --clean --distpath ../../electron/setup-extensions-dist setup-extensions.spec"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "homepage": ".",
  "build": {
    "appId": "com.electron.idaes-flowsheet-processor-ui",
    "extends": None,
    "asar": False,
    "productName": "IDAES-Flowsheet-Processor",
    "afterSign": "notarize.js",
    "nsis": {
      "oneClick": False,
      "allowToChangeInstallationDirectory": True,
    },
    "deb": {
      "depends": [
        "libgfortran5",
        "libgomp1",
        "liblapack3",
        "libblas3"
      ],
    },
    "files": [
      "dist/**/*",
      "build/**/*",
      "py_dist/**/*",
      "package.json",
      "setup-extensions-dist/**/*",
      "main.js"
    ],
    "directories": {
      "buildResources": "assets"
    },
    "extraResources": [
      "public/**/*"
    ],
    "mac": {
      "target": "dmg",
      "category": "utilities",
      "gatekeeperAssess": False,
      "hardenedRuntime": True,
      "entitlements": "build/entitlements.mac.inherit.plist",
      "entitlementsInherit": "build/entitlements.mac.inherit.plist",
    },
    "win": {
    },
    "linux": {
      "target": "Deb",
      "category": "Utility",
    }
  }
}

def getVersionDate():
    return datetime.today().strftime('%y.%m.%d')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", help="Project to create json file for. If not provided, default is WaterTAP.")
    args = parser.parse_args()
    project = args.project
    if project is None:
        project = "watertap"
    elif project.lower() == "idaes":
        project = "idaes"
    else:
        project = project.lower()

    version = getVersionDate()
    package_json = JSON_FRAMEWORK.copy()
    package_json["version"] = version
    package_json["author"] = "Michael Pesce <mpesce@lbl.gov>"


    package_json["build"]["win"]["target"] = "nsis"

    ## add artifact names with version
    package_json["build"]["nsis"]["artifactName"] = f"IDAES-Flowsheet-Processor_{version}_win64.exe"
    package_json["build"]["win"]["artifactName"] = f"IDAES-Flowsheet-Processor_{version}_win64.exe"
    package_json["build"]["deb"]["artifactName"] = f"IDAES-Flowsheet-Processor_{version}_amd64.deb"

    ## add icons
    if project == "watertap":
        icon = "build/nawi-logo.ico"
    else: ## TODO: create logos for each project
        icon = "build/nawi-logo.ico"
    

    package_json["build"]["mac"]["icon"] = icon
    package_json["build"]["win"]["icon"] = icon
    package_json["build"]["linux"]["icon"] = icon

    output_path = "electron/package.json"
    with open(output_path, "w") as f:
        json.dump(package_json, f)
