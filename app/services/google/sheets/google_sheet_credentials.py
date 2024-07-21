from oauth2client.service_account import ServiceAccountCredentials
from services.configuration_service import ConfigurationService

class GoogleSheetCredentials():

    def __init__(self,
                 configuration: ConfigurationService) -> None:
        self.configuration = configuration

    def get_credentials(self) -> ServiceAccountCredentials:
        scopes = self.configuration
        key_file = self.configuration
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file,
                                                                       scopes)
        return credentials
