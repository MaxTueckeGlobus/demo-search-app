import globus_sdk
from globus_sdk.tokenstorage import SimpleJSONFileAdapter
import os


class SearchApp:
    def __init__(self, env="sandbox"):
        os.environ["GLOBUS_SDK_ENVIRONMENT"] = env

        self.logged_in = False
        self.FILE_ADAPTER_PATH = os.path.expanduser("./tokens.json")
        self.CLIENT_ID = "a4598725-783f-4ca2-ba89-b6d289c27260"
        self.SCOPES = [
            globus_sdk.SearchClient.scopes.all,
            globus_sdk.AuthLoginClient.scopes.openid,
            globus_sdk.AuthLoginClient.scopes.email,
            globus_sdk.AuthLoginClient.scopes.profile,
        ]

        self.file_adapter = SimpleJSONFileAdapter(self.FILE_ADAPTER_PATH)
        self.auth_client = globus_sdk.NativeAppAuthClient(self.CLIENT_ID)


    def _do_login_flow(self, force_new_token=False):
        if self.file_adapter.file_exists():
            saved_token = self.file_adapter.get_token_data("search.api.globus.org")  
        else:
            saved_token = None

        if force_new_token or saved_token is None:
            self.auth_client.oauth2_start_flow(requested_scopes=self.SCOPES, refresh_tokens=True)
            authorize_url = self.auth_client.oauth2_get_authorize_url()

            print(f"Please go to this URL and login:\n\n{authorize_url}\n")
            auth_code = input("Please enter the code here: ").strip()

            tokens = self.auth_client.oauth2_exchange_code_for_tokens(auth_code)
            self.file_adapter.store(tokens)


    def _create_search_client(self):
        tokens = self.file_adapter.get_token_data("search.api.globus.org")

        self.refresh_authorizer = globus_sdk.RefreshTokenAuthorizer(
            tokens["refresh_token"],
            self.auth_client,
            access_token=tokens["access_token"],
            expires_at=tokens["expires_at_seconds"],
            on_refresh=self.file_adapter.on_refresh,
        )
        return globus_sdk.SearchClient(authorizer=self.refresh_authorizer)


    def login(self, force_new_token=False):
        self._do_login_flow(force_new_token=force_new_token)
        self.search_client = self._create_search_client()
        self.logged_in = True


    def logout(self):
        os.remove(self.FILE_ADAPTER_PATH)


    def whoami(self):
        if not self.logged_in:
            self.login()

        tokens = self.file_adapter.get_token_data("auth.globus.org")
        refresh_authorizer = globus_sdk.RefreshTokenAuthorizer(
            tokens["refresh_token"],
            self.auth_client,
            access_token=tokens["access_token"],
            expires_at=tokens["expires_at_seconds"],
            on_refresh=self.file_adapter.on_refresh,
        )
        ac = globus_sdk.AuthClient(authorizer=refresh_authorizer)
        return ac.userinfo()


    def create_index(self, display_name, description):
        response = self.search_client.create_index(
            display_name,
            description,
        )
        return response


    def delete_index(self, index_id):
        response = self.search_client.delete_index(index_id)
        return response


    def ingest_json_data(self, index_id, subject, json_data):
        ingest_data = {
            "ingest_type": "GMetaEntry",
            "ingest_data": {
                "subject": subject,
                "visible_to": ["public"],
                "content": json_data,
            },
        }

        response = self.search_client.ingest(index_id, ingest_data)
        return response


    def search(self, index_id, query, offset=0, limit=10):
        result = self.search_client.post_search(
            index_id, 
            query, 
            offset=offset, 
            limit=limit, 
        )

        return result


    def get_search_entry(self, index_id, subject):
        result = self.search_client.get_entry(
            index_id, 
            subject,
        )

        return result


    def delete_search_entry(self, index_id, subject):
        result = self.search_client.delete_entry(
            index_id, 
            subject,
        )

        return result
        