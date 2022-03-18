import json
from pathlib import Path
from typing import Optional
from zipfile import ZIP_DEFLATED, ZipFile

from patoolib import extract_archive

from dex_starr import INFO_EXTENSIONS, list_files, sanitize, yaml_setup
from dex_starr.console import CONSOLE
from dex_starr.metadata import FormatEnum, Metadata, parse_json, parse_xml, parse_yaml
from dex_starr.settings import SETTINGS, OutputFormatEnum

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


class Archive:
    def __init__(self, file: Path):
        self.source_file = file
        self.extracted_folder: Optional[Path] = None
        self.result_file: Optional[Path] = None

    def __extract_zip(self, extracted_folder: Path) -> bool:
        with ZipFile(self.source_file, "r") as zip_stream:
            zip_stream.extractall(path=extracted_folder)
        self.extracted_folder = extracted_folder
        return True

    def extract(self, processing_folder: Path) -> bool:
        extracted_folder = processing_folder.joinpath(self.source_file.stem)
        if extracted_folder.exists():
            CONSOLE.print(
                f"{extracted_folder.name} already exists in {extracted_folder.parent.name}",
                style="logging.level.error",
            )
            return False
        extracted_folder.mkdir(parents=True, exist_ok=True)

        if self.source_file.suffix in [".cbz"]:
            return self.__extract_zip(extracted_folder)

        output = extract_archive(
            str(self.source_file), outdir=str(extracted_folder), verbosity=-1, interactive=False
        )
        self.extracted_folder = Path(output)
        return True

    def _generate_result_filename(self, metadata: Metadata, collection_folder: Path) -> bool:
        publisher_filename = sanitize(metadata.publisher.title)
        publisher_folder = collection_folder.joinpath(publisher_filename)
        publisher_folder.mkdir(parents=True, exist_ok=True)

        series_filename = sanitize(metadata.series.title) + (
            f"-v{metadata.series.volume}" if metadata.series.volume > 1 else ""
        )
        series_folder = publisher_folder.joinpath(series_filename)
        series_folder.mkdir(exist_ok=True)

        if metadata.comic.format_ == FormatEnum.ANNUAL:
            comic_filename = f"{series_filename}-Annual-#{metadata.comic.number.zfill(2)}"
        elif metadata.comic.format_ == FormatEnum.DIGITAL_CHAPTER:
            comic_filename = f"{series_filename}-Chapter-#{metadata.comic.number.zfill(2)}"
        elif metadata.comic.format_ == FormatEnum.HARDCOVER:
            if metadata.comic.number != "0":
                comic_filename = f"{series_filename}-#{metadata.comic.number.zfill(2)}"
            else:
                if metadata.comic.title:
                    comic_filename = f"{series_filename}-{sanitize(metadata.comic.title)}"
                else:
                    comic_filename = series_filename
            comic_filename += "-HC"
        elif metadata.comic.format_ == FormatEnum.TRADE_PAPERBACK:
            if metadata.comic.number != "0":
                comic_filename = f"{series_filename}-#{metadata.comic.number.zfill(2)}"
            else:
                if metadata.comic.title:
                    comic_filename = f"{series_filename}-{sanitize(metadata.comic.title)}"
                else:
                    comic_filename = series_filename
            comic_filename += "-TP"
        else:
            comic_filename = f"{series_filename}-#{metadata.comic.number.zfill(3)}"

        self.result_file = series_folder.joinpath(comic_filename + ".cbz")
        if self.result_file.exists():
            return False
        return True

    def _rename_images(self):
        image_list = list_files(self.extracted_folder, filter_=IMAGE_EXTENSIONS)
        list_length = len(str(len(image_list)))
        for index, img_file in enumerate(image_list):
            img_file.rename(
                self.extracted_folder.joinpath(
                    f"{self.result_file.stem}-{str(index).zfill(list_length)}{img_file.suffix}"
                )
            )

    def archive(self, metadata: Metadata, collection_folder: Path) -> bool:
        if not self._generate_result_filename(metadata, collection_folder):
            return False
        CONSOLE.print(
            f"Bundling up as {self.result_file.relative_to(collection_folder)}",
            style="logging.level.info",
        )
        self._rename_images()

        zipped_file = self.extracted_folder.parent.joinpath(self.result_file.name)
        if zipped_file.exists():
            return False

        with ZipFile(zipped_file, "w", ZIP_DEFLATED) as zip_stream:
            for file in list_files(
                self.extracted_folder, filter_=[*IMAGE_EXTENSIONS, ".json", ".yaml", ".xml"]
            ):
                zip_stream.write(file, file.relative_to(self.extracted_folder))

        zipped_file.rename(self.result_file)
        return True

    def save_info(self, metadata: Metadata):
        info_file = self.extracted_folder / f"ComicInfo.{SETTINGS.output_format.name.lower()}"
        CONSOLE.print(f"Saving Info File as {info_file.name}", style="logging.level.info")

        with info_file.open("w", encoding="UTF-8") as stream:
            if SETTINGS.output_format == OutputFormatEnum.JSON:
                json.dump(metadata.dump(), stream, default=str, indent=2, ensure_ascii=False)
            elif SETTINGS.output_format == OutputFormatEnum.YAML:
                yaml_setup().dump(metadata.dump(), stream)

    def parse_info(self) -> Metadata:
        info_files = list_files(self.extracted_folder, filter_=INFO_EXTENSIONS)
        CONSOLE.print(
            f"Info File/s Found: {[x.name for x in info_files]}", style="logging.level.info"
        )
        metadata = None
        if ".json" in [x.suffix for x in info_files]:
            metadata = parse_json([x for x in info_files if x.suffix == ".json"][0])
        elif ".yaml" in [x.suffix for x in info_files]:
            metadata = parse_yaml([x for x in info_files if x.suffix == ".yaml"][0])
        elif ".xml" in [x.suffix for x in info_files]:
            metadata = parse_xml([x for x in info_files if x.suffix == ".xml"][0])
        if not metadata:
            metadata = Metadata.create()
        return metadata
