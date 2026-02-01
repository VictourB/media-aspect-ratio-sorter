import argparse
import pathlib
import shutil
import logging
import collections
from typing import Tuple
from PIL import Image, UnidentifiedImageError
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core import config as hachoir_config

hachoir_config.quiet = True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sort_log.txt"),
        logging.StreamHandler()
    ]

)
class MediaSorter:
    """Tool to organize images and video by aspect ratio."""

    def __init__(self, target_path: pathlib.Path, limiter: int = 10, move_files: bool = False):
        self.target_path = target_path
        self.limiter = int(limiter)
        self.move_files = move_files
        self.output_path = self._generate_unique_path()

        self.stats = collections.Counter()
        self.total_size_bytes = 0

    def _generate_unique_path(self) -> pathlib.Path:
        """Generates a path name to prevent overwriting data."""
        base_name = f"{self.target_path.name}_sorted_L{self.limiter}"
        candidate = self.target_path.parent / base_name

        if not candidate.exists():
            return candidate

        counter = 1
        while True:
            candidate = self.target_path.parent / f"{base_name} ({counter})"
            if not candidate.exists():
                return candidate
            counter += 1


    def _apply_limiter(self, ratio_val: float) -> Tuple[int, int]:
        """Calculates simplified aspect ratios using the Farey sequence."""
        lower, upper = (0, 1), (1, 0)
        while True:
            mediant = (lower[0] + upper[0], lower[1] + upper[1])
            if ratio_val * mediant[1] > mediant[0]:
                if self.limiter < mediant[1]: return upper
                lower = mediant
            elif ratio_val * mediant[1] == mediant[0]:
                return mediant
            else:
                if self.limiter < mediant[1]: return lower
                upper = mediant

    @staticmethod
    def _get_dimensions(file_path: pathlib.Path) -> Tuple[int, int]:
        if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}:
            try:
                with Image.open(file_path) as img:
                    return img.width, img.height
            except (UnidentifiedImageError, IOError):
                pass

        parser = createParser(str(file_path))
        if parser:
            with parser:
                metadata = extractMetadata(parser)
                if metadata and metadata.has('width'):
                    return int(metadata.get('width')), int(metadata.get('height'))

        raise ValueError("Unsupported format or missing dimension metadata.")

    def run(self) -> None:
        """Does the sorting process."""

        if not self.target_path.is_dir():
            logging.error(f"Target path {self.target_path} is not a directory.")
            return

        self.output_path.mkdir(parents=True, exist_ok=True)
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp4', '.mkv', '.mov'}

        logging.info(f"Starting sort in: {self.target_path}")

        for file in self.target_path.iterdir():
            if file.suffix.lower() not in valid_extensions:
                continue

            try:
                width, height = self._get_dimensions(file)
                x, y = self._apply_limiter(width / height)

                ratio_folder = f"{x}X{y}"
                subdir = self.output_path / ratio_folder
                subdir.mkdir(exist_ok=True)

                destination = subdir / file.name
                file_size = file.stat().st_size

                if self.move_files:
                    shutil.move(str(file), str(destination))
                else:
                    shutil.copy2(str(file), str(destination))

                self.stats[ratio_folder]+= 1
                self.total_size_bytes += file_size
                logging.info(f"Sorted: {file.name} -> {ratio_folder}")

            except Exception as e:
                logging.error(f"Skipping {file.name}: {e}")

        self._print_summary()


    def _print_summary(self):
        """Displays final processing stats"""
        print("\n" + "="*30)
        print("SORT SUMMARY")
        print("="*30)
        total_files = sum(self.stats.values())
        size_mb = self.total_size_bytes / (1024 * 1024)

        print(f"Total Files Processed: {total_files}")
        print(f"Total Data handled:    {size_mb:.2f} MB")

        if self.stats:
            most_common = self.stats.most_common(1)[0]
            print(f"Most Common Ratio: {most_common[0]} ({most_common[1]} files)")
        print("="*30 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Professional Multi-Media Sorter")

    parser.add_argument(
        "directory",
        help="Target directory",
        type=str,
        nargs="?",
        default="."
    )

    parser.add_argument(
        "limiter",
        help="Ratio limiter (Default: 10)",
        type=int,
        nargs="?",
        default=10
    )

    parser.add_argument(
        "--move",
        action="store_true",
        help="Move instead of copy"
    )

    args = parser.parse_args()
    target = pathlib.Path(args.directory)

    sorter = MediaSorter(target, args.limiter, args.move)
    sorter.run()

if __name__ == "__main__":
    main()
