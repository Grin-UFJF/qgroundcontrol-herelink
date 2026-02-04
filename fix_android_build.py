import os
import shutil
import subprocess
import sys

# Paths
QT_ANDROID_BIN = r"C:\Qt\5.15.2\android\bin\androiddeployqt.exe"
DEPLOY_SETTINGS = r"C:\Users\viki\Documents\qgroundcontrol-herelink\build\Qt_5_15_2_for_Android_Multi_Abi-Debug\android-Herelink-QGroundControl-deployment-settings.json"
OUTPUT_DIR = r"C:\Users\viki\Documents\qgroundcontrol-herelink\build\Qt_5_15_2_for_Android_Multi_Abi-Debug\android-build"
# This directory is where androiddeployqt looks for the source template
PACKAGE_SOURCE_DIR = r"C:\Users\viki\Documents\qgroundcontrol-herelink\build\Qt_5_15_2_for_Android_Multi_Abi-Debug\ANDROID_PACKAGE_SOURCE_DIR"
SRC_DIR = r"C:\Users\viki\Documents\qgroundcontrol-herelink\android"
JDK_PATH = r"C:\Program Files\Android\Android Studio\jbr"

def copy_sources():
    print(f"Copying sources from {SRC_DIR} to {PACKAGE_SOURCE_DIR}...")
    if not os.path.exists(PACKAGE_SOURCE_DIR):
        os.makedirs(PACKAGE_SOURCE_DIR)
    
    # Recursive copy
    for item in os.listdir(SRC_DIR):
        s = os.path.join(SRC_DIR, item)
        d = os.path.join(PACKAGE_SOURCE_DIR, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

def run_android_deploy_qt():
    print("Running androiddeployqt...")
    # Setup environment with JAVA_HOME
    env = os.environ.copy()
    env["JAVA_HOME"] = JDK_PATH
    # Add JDK bin to PATH as well just in case
    env["PATH"] = os.path.join(JDK_PATH, "bin") + os.pathsep + env["PATH"]

    cmd = [
        QT_ANDROID_BIN,
        "--input", DEPLOY_SETTINGS,
        "--output", OUTPUT_DIR,
        "--android-platform", "android-36",
        "--jdk", JDK_PATH,
        "--gdbserver"
    ]
    # Allow androiddeployqt to fail (since it tries to build and fails due to the deprecated flag)
    # We will fix the flag and rebuild manually.
    subprocess.run(cmd, env=env, check=False)

def patch_gradle_properties():
    print("Patching gradle.properties...")
    prop_file = os.path.join(OUTPUT_DIR, "gradle.properties")
    if not os.path.exists(prop_file):
        print("Error: gradle.properties not found!")
        return

    with open(prop_file, "r") as f:
        lines = f.readlines()

    # Remove deprecated AGP property if present
    new_lines = []
    removed = False
    for line in lines:
        if line.strip().startswith("android.bundle.enableUncompressedNativeLibs="):
            removed = True
            continue
        new_lines.append(line)

    with open(prop_file, "w") as f:
        f.writelines(new_lines)
    
    if removed:
        print("Removed deprecated android.bundle.enableUncompressedNativeLibs property.")
    else:
        print("No deprecated property found.")

def _resolve_android_package_name():
    # Prefer custom package if present
    candidates = [
        r"C:\Users\viki\Documents\qgroundcontrol-herelink\custom\custom.pri",
        r"C:\Users\viki\Documents\qgroundcontrol-herelink\custom-example\custom.pri",
        r"C:\Users\viki\Documents\qgroundcontrol-herelink\QGCCommon.pri",
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("QGC_ANDROID_PACKAGE"):
                    # handle: QGC_ANDROID_PACKAGE = "org.example.app"
                    parts = line.split("=")
                    if len(parts) >= 2:
                        value = parts[1].strip().strip('"').strip("'")
                        if value:
                            return value
    # Fallback
    return "org.mavlink.qgroundcontrol"

def patch_android_manifest_package():
    print("Patching AndroidManifest.xml package...")
    manifest_file = os.path.join(OUTPUT_DIR, "AndroidManifest.xml")
    if not os.path.exists(manifest_file):
        print("Error: AndroidManifest.xml not found!")
        return None

    package_name = _resolve_android_package_name()

    with open(manifest_file, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("%%QGC_INSERT_PACKAGE_NAME%%", package_name)
    content = content.replace('package="org.mavlink.qgroundcontrol"', f'package="{package_name}"')

    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f'AndroidManifest.xml package set to "{package_name}".')
    return package_name

def patch_build_gradle_namespace_and_features(package_name):
    print("Patching build.gradle namespace/buildFeatures...")
    gradle_file = os.path.join(OUTPUT_DIR, "build.gradle")
    if not os.path.exists(gradle_file):
        print("Error: build.gradle not found!")
        return
    if not package_name:
        print("Error: Package name not provided.")
        return

    with open(gradle_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    has_namespace = any(l.strip().startswith("namespace ") for l in lines)
    has_build_features = any(l.strip().startswith("buildFeatures {") for l in lines)

    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if not inserted and line.strip() == "android {":
            if not has_namespace:
                new_lines.append(f'    namespace "{package_name}"\n')
            if not has_build_features:
                new_lines.append("    buildFeatures {\n")
                new_lines.append("        aidl true\n")
                new_lines.append("    }\n")
            inserted = True

    if not inserted:
        print("Error: Could not find android { block to insert namespace.")
        return

    with open(gradle_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    if not has_namespace:
        print(f'Added namespace "{package_name}".')
    else:
        print("Namespace already present.")
    if not has_build_features:
        print("Added buildFeatures { aidl true }.")
    else:
        print("buildFeatures already present.")

def run_gradle_build():
    print("Running Gradle build...")
    # Setup environment with JAVA_HOME
    env = os.environ.copy()
    env["JAVA_HOME"] = JDK_PATH
    env["PATH"] = os.path.join(JDK_PATH, "bin") + os.pathsep + env["PATH"]

    # Use gradlew.bat in the output directory
    gradlew = os.path.join(OUTPUT_DIR, "gradlew.bat")
    
    # Check if gradlew exists, if not use local gradle or fail
    if not os.path.exists(gradlew):
        print(f"Error: {gradlew} not found.")
        return

    # run assembleDebug
    cmd = [gradlew, "assembleDebug"]
    subprocess.check_call(cmd, cwd=OUTPUT_DIR, env=env)

if __name__ == "__main__":
    try:
        copy_sources()
        run_android_deploy_qt()
        patch_gradle_properties()
        package_name = patch_android_manifest_package()
        patch_build_gradle_namespace_and_features(package_name)
        run_gradle_build()
        print("Build successful!")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)
