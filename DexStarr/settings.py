from configparser import ConfigParser
from pathlib import Path


class Settings:
    def __init__(self):
        self.root_folder = Path.home().joinpath("Comics").resolve()
        self.comicvine_api_key = ""
        self.league_api_key = ""
        self.league_client_id = ""
        self.metron_username = ""
        self.metron_password = ""

        self.config = ConfigParser()
        self.config.optionxform = str
        folder = Path.home().joinpath(".config").joinpath("Dex-Starr")
        self.settings_file = folder.joinpath("settings.ini")

        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)

        if not self.settings_file.exists():
            self.save()
        else:
            self.load()

        self.collection_folder = self.root_folder.joinpath("Collection")
        self.collection_folder.mkdir(parents=True, exist_ok=True)
        self.import_folder = self.root_folder.joinpath("Import")
        self.import_folder.mkdir(parents=True, exist_ok=True)
        self.processing_folder = self.root_folder.joinpath("Processing")
        self.processing_folder.mkdir(parents=True, exist_ok=True)

    def save(self) -> None:
        if not self.config.has_section("General"):
            self.config.add_section("General")
        self.config["General"]["Root Folder"] = str(self.root_folder)

        if not self.config.has_section("Comicvine"):
            self.config.add_section("Comicvine")
        self.config["Comicvine"]["API Key"] = self.comicvine_api_key

        if not self.config.has_section("League of Comic Geeks"):
            self.config.add_section("League of Comic Geeks")
        self.config["League of Comic Geeks"]["API Key"] = self.league_api_key
        self.config["League of Comic Geeks"]["Client ID"] = self.league_client_id

        if not self.config.has_section("Metron"):
            self.config.add_section("Metron")
        self.config["Metron"]["Username"] = self.metron_username
        self.config["Metron"]["Password"] = self.metron_password

        with self.settings_file.open("w") as config_file:
            self.config.write(config_file)

    def load(self) -> None:
        self.config.read(self.settings_file)

        if self.config.has_option("General", "Root Folder"):
            self.root_folder = Path(self.config["General"]["Root Folder"]).resolve()

        if self.config.has_option("Comicvine", "API Key"):
            self.comicvine_api_key = self.config["Comicvine"]["API Key"]

        if self.config.has_option("League of Comic Geeks", "API Key"):
            self.league_api_key = self.config["League of Comic Geeks"]["API Key"]
        if self.config.has_option("League of Comic Geeks", "Client ID"):
            self.league_client_id = self.config["League of Comic Geeks"]["Client ID"]

        if self.config.has_option("Metron", "Username"):
            self.metron_username = self.config["Metron"]["Username"]
        if self.config.has_option("Metron", "Password"):
            self.metron_password = self.config["Metron"]["Password"]
