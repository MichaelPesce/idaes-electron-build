from datetime import datetime
import argparse
import json
import pathlib
import os
from importlib.metadata import version

JSON_FRAMEWORK = {
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
    "electron-build-lin": "npm run remove-previous-dist && electron-builder -l || electron-builder -l",
    "dist:mac": "npm run build-replace-backend && npm run build-frontend && npm run electron-build-mac",
    "dist:win": "npm run build-replace-backend-win && npm run build-frontend-win && npm run electron-build-win",
    "dist:lin": "npm run build-replace-backend && npm run build-frontend && npm run electron-build-lin",
    "remove-previous-backend-build": "rm -r py_dist/*",
    "remove-previous-backend-build-win": "rd /S /Q py_dist",
    "remove-previous-dist": "rm -r dist/*",
    "remove-previous-dist-win": "rd /S /Q dist",
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
    "extends": None,
    "asar": False,
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

def generatePackageJson(project, ui_version, artifact_name, author, output_path="../electron/package.json"):
    ## If email is empty what to use hmmm
    if "<>" in author:
        author.replace("<>", "<unknown@email.com>")
        
    package_json = JSON_FRAMEWORK.copy()
    package_json["version"] = ui_version
    package_json["author"] = author
    package_json["email"] = author
    if project == "idaes":
        package_json["name"] = "idaes-flowsheet-processor-ui"
        package_json["build"]["productName"] = "IDAES-Flowsheet-Processor"
        package_json["build"]["appId"] = "com.electron.idaes-flowsheet-processor-ui"
        icon = "build/idaes-logo.ico"
    elif project == "watertap":
        package_json["name"] = "watertap-flowsheet-processor-ui"
        package_json["build"]["productName"] = "WaterTAP-Flowsheet-Processor"
        package_json["build"]["appId"] = "com.electron.watertap-flowsheet-processor-ui"
        icon = "build/nawi-logo.ico"
    elif project == "prommis":
        package_json["name"] = "prommis-flowsheet-processor-ui"
        package_json["build"]["productName"] = "PROMMIS-Flowsheet-Processor"
        package_json["build"]["appId"] = "com.electron.prommis-flowsheet-processor-ui"
        icon = "build/prommis-logo.ico"

    package_json["build"]["mac"]["icon"] = icon
    package_json["build"]["win"]["icon"] = icon
    package_json["build"]["linux"]["icon"] = icon

    package_json["build"]["win"]["target"] = "nsis"

    ## add artifact names with version
    package_json["build"]["nsis"]["artifactName"] = f"{artifact_name}_{ui_version}_win64.exe"
    package_json["build"]["win"]["artifactName"] = f"{artifact_name}_{ui_version}_win64.exe"
    package_json["build"]["mac"]["artifactName"] = f"{artifact_name}_{ui_version}_arm64.dmg"
    package_json["build"]["deb"]["artifactName"] = f"{artifact_name}_{ui_version}_amd64.deb"

    working_dir = pathlib.Path(__file__).parent.resolve()
    package_json_path = os.path.join(working_dir,output_path)
    with open(package_json_path, "w") as f:
        json.dump(package_json, f)

def setEnvVariables(project, ui_version, project_version):
    working_dir = pathlib.Path(__file__).parent.resolve()
    hook_env_path = os.path.join(working_dir,"../pyinstaller/hooks/.env")
    electron_env_path = os.path.join(working_dir,"../electron/.env")
    react_app_env_path = os.path.join(working_dir,"../electron/idaes-flowsheet-processor-ui/frontend/.env")

    with open(hook_env_path, "w") as f:
        f.write(f"project={project}")

    with open(electron_env_path, "w") as f:
        f.write(f"project={project}")

    with open(react_app_env_path, "w") as f:
        f.write(f"REACT_APP_THEME={project}\nREACT_APP_BUILD_VERSION={ui_version}\nREACT_APP_PROJECT_VERSION={project_version}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", help="Project to create json file for. If not provided, default is WaterTAP.")
    parser.add_argument("-bv", "--build_version", help="Build version, typically in date format (yy.mm.dd). If not provided, will use current date.")
    parser.add_argument("-a", "--artifact_name", help="Artifact name. If not provided, will use provided project to create artifact name.")
    parser.add_argument("-pv", "--project_version", help="Project version, ie the version of WaterTAP, IDAES, or PROMMIS that is installed.")
    parser.add_argument("-au", "--author", help="Author who created the build.")
    args = parser.parse_args()
    project = args.project
    ui_version = args.build_version
    artifact_name = args.artifact_name
    project_version = args.project_version
    author = args.author
    if ui_version is None:
        ui_version = getVersionDate()
    if artifact_name is None:
        artifact_name = f"{project}-Flowsheet-Processor"
    if author is None:
        author = "unknown"

    valid_projects = ["watertap", "prommis", "idaes"]
    if project is not None:
        project = project.lower()
    if project not in valid_projects:
        print(f"project provided: {project} is not a valid project. Must be one of {valid_projects}. Defaulting to watertap")
        project = "watertap"
    if project_version is None:
        print(f"project version is none. Attempting to get project version from python environment")
        if project == "idaes":
            project_version = version("idaes_pse")
        else:
            project_version = version(project)
        print(f"using project version: {project_version}")

    generatePackageJson(project=project, ui_version=ui_version, author=author, artifact_name=artifact_name)
    setEnvVariables(project=project, ui_version=ui_version, project_version=project_version)
