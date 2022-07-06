import shutil
from pathlib import Path
from typing import Optional
from zipfile import ZIP_DEFLATED, ZipFile

from patoolib import extract_archive

from dex_starr import IMAGE_EXTENSIONS, SUPPORTED_INFO_FILES, get_cache_root, list_files
from dex_starr.console import CONSOLE
from dex_starr.metadata.metadata import Metadata


class Archive:
    def __init__(self, file: Path):
        self.source_file = file
        self.extracted_folder: Optional[Path] = None
        self.result_file: Optional[Path] = None

    def _extract_zip(self, extracted_folder: Path) -> bool:
        with ZipFile(self.source_file, "r") as zip_stream:
            zip_stream.extractall(path=extracted_folder)
        self.extracted_folder = extracted_folder
        return True

    def extract(self) -> bool:
        extracted_folder = get_cache_root() / self.source_file.stem
        if extracted_folder.exists():
            CONSOLE.print(
                f"{extracted_folder.name} already exists in {extracted_folder.parent.name}",
                style="logging.level.error",
            )
            return False
        extracted_folder.mkdir(parents=True, exist_ok=True)

        if self.source_file.suffix in [".cbz"]:
            return self._extract_zip(extracted_folder)

        output = extract_archive(
            str(self.source_file), outdir=str(extracted_folder), verbosity=-1, interactive=False
        )
        self.extracted_folder = Path(output)
        return True

    def _rename_images(self):
        image_list = list_files(self.extracted_folder, filter_=IMAGE_EXTENSIONS)
        list_length = len(str(len(image_list)))
        for index, img_file in enumerate(image_list):
            img_file.rename(
                self.extracted_folder
                / f"{self.result_file.stem}-{str(index).zfill(list_length)}{img_file.suffix}"
            )

    def archive(self, metadata: Metadata, collection_folder: Path) -> bool:
        series_folder = collection_folder / metadata.publisher.file_name / metadata.series.file_name
        series_folder.mkdir(parents=True, exist_ok=True)
        self.result_file = (
            series_folder / f"{metadata.series.file_name}{metadata.issue.file_name}.cbz"
        )
        self._rename_images()

        zipped_file = self.extracted_folder.parent / self.result_file.name
        if zipped_file.exists():
            return False

        with ZipFile(zipped_file, "w", ZIP_DEFLATED) as zip_stream:
            for file in list_files(self.extracted_folder):
                if file.suffix in IMAGE_EXTENSIONS:
                    zip_stream.write(file, file.relative_to(self.extracted_folder))
                elif file.name in SUPPORTED_INFO_FILES:
                    zip_stream.write(file, file.relative_to(self.extracted_folder))

        return shutil.move(zipped_file, self.result_file)
