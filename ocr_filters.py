import click
from pathlib import Path
from PIL import Image
import pytesseract


def extract_subreddits_from_text(text: str) -> list:
    # Changed: split lines preserving order and remove duplicates.
    seen = set()
    ordered = []
    for line in text.splitlines():
        line_stripped = line.strip()
        if line_stripped and line_stripped not in seen:
            seen.add(line_stripped)
            ordered.append(line_stripped)
    return ordered


def process_image(image_path: Path) -> list:
    try:
        img = Image.open(image_path)
        # Crop image: remove a bit more than a third from the top but less than a quarter
        width, height = img.size
        top = int(height * 0.30)  # changed: crop at 30% of the height
        bottom = height - (height // 5)
        cropped_img = img.crop((0, top, width, bottom))
        text = pytesseract.image_to_string(cropped_img)
        return extract_subreddits_from_text(text)
    except Exception as e:
        click.echo(f"Error processing {image_path}: {e}")
        return []


@click.command()
@click.argument("screenshot_dir", type=click.Path(exists=True, file_okay=False))
def ocr_filters(screenshot_dir: str):
    """
    Process screenshots from SCREENSHOT_DIR and output deduplicated subreddits.
    """
    screenshots = list(Path(screenshot_dir).glob("*.[pj][np]g"))
    if not screenshots:
        click.echo("No image files found in the directory.")
        return

    all_subs = set()
    for img_file in screenshots:
        click.echo(f"Processing {img_file}...")
        subs = process_image(img_file)
        all_subs.update(subs)

    if all_subs:
        click.echo("Subreddits extracted:")
        for sub in sorted(all_subs):
            click.echo(sub)  # changed: removed 'r/' prefix
    else:
        click.echo("No subreddits found.")


if __name__ == "__main__":
    ocr_filters()
