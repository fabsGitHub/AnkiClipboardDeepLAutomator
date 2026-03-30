import platform
import subprocess
import sys
import importlib.util
from logging_setup import setup_logging, log_info, log_warning, log_error


def is_package_installed(package_name):
    """Check if a package is installed using importlib.util.find_spec."""
    # Mapping von Paketnamen in requirements.txt zu den tatsächlichen Modulnamen
    package_mapping = {
        "python-dotenv": "python_dotenv",
        "pyobjc": "pyobjc",
    }

    # Verwende den tatsächlichen Modulnamen
    actual_package_name = package_mapping.get(package_name, package_name)
    spec = importlib.util.find_spec(actual_package_name)
    return spec is not None


def install_dependencies(logger):
    """
    Installs all required dependencies for the project based on the platform.
    Returns True if all dependencies are installed (whether already present or newly installed),
    False if installation fails.
    """
    log_info(logger, "🔧 Starting dependency installation check")

    packages = [
        "requests>=2.25.1",
        "python-dotenv>=0.19.0",
        "deepl>=1.5.0",
        "pynput>=1.7.3",
        "pygame>=2.0.1",
    ]

    if platform.system() == "Darwin":  # macOS
        packages.append("pyobjc>=7.3")
    elif platform.system() == "Windows":
        packages.append("win10toast>=0.9")

    log_info(logger, f"📋 Checking {len(packages)} packages...")
    packages_to_install = []

    for package in packages:
        package_name = package.split(">=")[0].split("==")[0]
        if is_package_installed(package_name):
            log_info(logger, f"✅ {package_name} is already installed")
        else:
            log_warning(logger, f"❌ {package_name} is missing")
            packages_to_install.append(package)

    if not packages_to_install:
        log_info(logger, "✨ All dependencies are already installed!")
        return True

    log_info(logger, f"\n📦 Installing {len(packages_to_install)} missing packages...")
    log_info(
        logger,
        "ℹ️ This might take a few minutes depending on your internet connection...",
    )

    failed_packages = []

    for package in packages_to_install:
        package_name = package.split(">=")[0].split("==")[0]
        log_info(logger, f"\n📥 Installing {package}...")

        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            log_info(logger, f"✅ Successfully installed {package_name}")
        except subprocess.CalledProcessError as e:
            log_error(logger, f"❌ Failed to install {package_name}. Error: {e}", e)
            failed_packages.append(package_name)

    if failed_packages:
        log_warning(
            logger,
            f"💡 The following packages failed to install: {', '.join(failed_packages)}",
        )
        log_info(
            logger,
            "💡 Tip: Try installing them manually using: pip install <package_name>",
        )
        return False

    log_info(logger, "\n✨ All dependencies installed successfully!")
    return True
