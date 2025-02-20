import logging
import subprocess
from cli_commands import cli
import pytesseract
from rich.console import Console
from utils.device import get_device_id  # Added import

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def check_adb():
    try:
        subprocess.run(["adb", "version"], check=True, capture_output=True)
        console.print("[green]✅ ADB is available[/green]")
    except Exception as e:
        console.print(f"[red]❌ ADB not found or not working properly: {e}[/red]")


def check_tesseract():
    try:
        tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
        subprocess.run([tesseract_cmd, "--version"], check=True, capture_output=True)
        console.print("[green]✅ Tesseract OCR is available[/green]")
    except Exception as e:
        console.print(
            f"[red]❌ Tesseract OCR not found or not working properly: {e}[/red]"
        )


# New function to check if Android device is connected
def check_android_device():
    try:
        device = get_device_id()
        console.print(f"[green]✅ Android device connected: {device}[/green]")
    except Exception as e:
        console.print(f"[red]❌ No Android device connected: {e}[/red]")


def pre_run_setup():
    console.print("\n[bold cyan]🔧 Performing pre-run setup...[/bold cyan]")
    check_adb()
    check_tesseract()
    check_android_device()  # Added device check
    console.print("[bold cyan]✨ Setup complete![/bold cyan]\n")


if __name__ == "__main__":
    pre_run_setup()
    cli()
