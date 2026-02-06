import os
import subprocess
import sys

# Configuration
BUILD_DIR = r"C:\Users\viki\Documents\qgroundcontrol-herelink\build\Qt_5_15_2_for_Android_Multi_Abi-Debug"
MAKE_EXE = r"C:\Users\viki\AppData\Local\Android\Sdk\ndk\21.3.6528147\prebuilt\windows-x86_64\bin\make.exe"
QMAKE_EXE = r"C:\Qt\5.15.2\android\bin\qmake.exe"
FIX_SCRIPT = r"C:\Users\viki\Documents\qgroundcontrol-herelink\fix_android_build.py"
ADB_EXE = r"C:\Users\viki\AppData\Local\Android\Sdk\platform-tools\adb.exe"
APK_PATH = r"C:\Users\viki\Documents\qgroundcontrol-herelink\build\Qt_5_15_2_for_Android_Multi_Abi-Debug\android-build\build\outputs\apk\debug\android-build-debug.apk"
DEVICE_ID = "4e8f4dd9"
ANDROID_NDK_ROOT = r"C:\Users\viki\AppData\Local\Android\Sdk\ndk\21.3.6528147"
ANDROID_SDK_ROOT = r"C:\Users\viki\AppData\Local\Android\Sdk"

def run_step(description, cmd, cwd=None, env=None, check=True):
    print(f"=== {description} ===")
    print(f"Running: {' '.join(cmd)}")
    
    # Merge provided env with system env, or use system env if None
    # We always want to inject our Android vars
    run_env = env if env is not None else os.environ.copy()
    run_env["ANDROID_NDK_ROOT"] = ANDROID_NDK_ROOT
    run_env["ANDROID_SDK_ROOT"] = ANDROID_SDK_ROOT
    
    try:
        subprocess.run(cmd, cwd=cwd, env=run_env, check=check, shell=False)
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}: {e}")
        # If build fails, we usually stop. But if user expects 'make' to succeed and 'androiddeployqt' to fail (which is handled by fix script potentially),
        # we still want to ensure 'make' succeeded for the C++ code.
        # The user said "vai dar erro no final" referring to their current flow.
        # My automate script replaces their flow.
        # If 'make' fails, the C++ code is broken, so we should probably stop.
        sys.exit(1)

def main():
    # 0. Run qmake (Update Makefile and MOCs)
    # This ensures that changes to .h files (like Q_PROPERTY) are picked up.
    run_step("Updating Project (qmake)", [QMAKE_EXE, r"C:\Users\viki\Documents\qgroundcontrol-herelink\qgroundcontrol.pro"], cwd=BUILD_DIR)

    # 1. Run Make (Compile C++)
    run_step("Compiling C++ (Make)", [MAKE_EXE], cwd=BUILD_DIR)

    # 2. Run Fix Script (Package & Build APK)
    # fix_android_build.py expects to be run? It assumes paths.
    run_step("Packaging & Building APK (fix_android_build.py)", [sys.executable, FIX_SCRIPT])

    # 3. Install APK via ADB
    run_step("Installing APK", [ADB_EXE, "-s", DEVICE_ID, "install", "-r", APK_PATH])

    print("\n=== All Steps Completed Successfully! ===")

if __name__ == "__main__":
    main()
