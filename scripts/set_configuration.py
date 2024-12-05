from datetime import datetime
import argparse
import json
import pathlib
import os

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
    "move-frontend-build-win": "move /Y idaes-flowsheet-processor-ui/frontend/build build",
    "build-frontend": "npm --prefix idaes-flowsheet-processor-ui/frontend run build",
    "build-frontend-win": "npm --prefix idaes-flowsheet-processor-ui/frontend run build && npm run move-frontend-build-win || npm run move-frontend-build-win",
    "build-backend": "cd ../pyinstaller && pyinstaller -y --clean --distpath ../electron/py_dist main.spec",
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
    "get-extensions-installer": "cd ../pyinstaller && pyinstaller -y --clean --distpath ../electron/setup-extensions-dist setup-extensions.spec"
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

def generatePackageJson(version, project, output_path="../electron/package.json", author="Michael Pesce <mpesce@lbl.gov>"):
    
    package_json = JSON_FRAMEWORK.copy()
    package_json["version"] = version
    package_json["author"] = author


    package_json["build"]["win"]["target"] = "nsis"

    ## add artifact names with version
    package_json["build"]["nsis"]["artifactName"] = f"{project}-Flowsheet-Processor_{version}_win64.exe"
    package_json["build"]["win"]["artifactName"] = f"{project}-Flowsheet-Processor_{version}_win64.exe"
    package_json["build"]["deb"]["artifactName"] = f"{project}-Flowsheet-Processor_{version}_amd64.deb"

    ## add icons
    if project == "watertap":
        icon = "build/nawi-logo.ico"
    else: ## TODO: create logos for each project
        icon = "build/nawi-logo.ico"
    

    package_json["build"]["mac"]["icon"] = icon
    package_json["build"]["win"]["icon"] = icon
    package_json["build"]["linux"]["icon"] = icon

    working_dir = pathlib.Path(__file__).parent.resolve()
    package_json_path = os.path.join(working_dir,output_path)
    with open(package_json_path, "w") as f:
        json.dump(package_json, f)

def setEnvVariables(version, project):
    working_dir = pathlib.Path(__file__).parent.resolve()
    hook_env_path = os.path.join(working_dir,"../pyinstaller/hooks/.env")
    react_app_env_path = os.path.join(working_dir,"../electron/idaes-flowsheet-processor-ui/frontend/.env")

    with open(hook_env_path, "w") as f:
        f.write(f"project={project}")

    with open(react_app_env_path, "w") as f:
        f.write(f"REACT_APP_THEME={project}\nREACT_APP_BUILD_VERSION={version}")

if __name__ == "__main__":
    ## TODO: add argument for version number
    ## - if null, use the function here. otherwise use the argument
    ## TODO: also add this version nubmer as an environment variable in the react app frontend (for splash page)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", help="Project to create json file for. If not provided, default is WaterTAP.")
    parser.add_argument("-v", "--version", help="Build version, typically in date format (yy.mm.dd). If not provided, will use current date.")
    args = parser.parse_args()
    project = args.project
    version = args.version
    if version is None:
        version = getVersionDate()
    valid_projects = ["watertap", "prommis", "idaes"]
    if project is not None:
        project = project.lower()
    if project not in valid_projects:
        print(f"project provided: {project} is not a valid project. Must be one of {valid_projects}. Defaulting to watertap")
        project = "watertap"

    generatePackageJson(project, version)
    setEnvVariables(project, version)
