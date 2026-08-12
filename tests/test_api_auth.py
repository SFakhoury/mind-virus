from unittest.mock import patch
import unittest

from mind_virus.api_auth import APIAuthenticator


class APIAuthenticatorTests(unittest.TestCase):
    def test_disabled_local_auth_allows_requests(self):
        self.assertTrue(APIAuthenticator().authorize(None))

    def test_configured_token_is_required(self):
        auth = APIAuthenticator("secret-token")
        self.assertFalse(auth.authorize(None))
        self.assertFalse(auth.authorize("wrong"))
        self.assertTrue(auth.authorize("secret-token"))

    def test_production_rejects_missing_access_token(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "required"):
                APIAuthenticator.from_environment(required=True)

    def test_provider_key_is_never_used_as_app_authentication(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "provider-secret"}, clear=True):
            self.assertFalse(APIAuthenticator.from_environment().enabled)


if __name__ == "__main__":
    unittest.main()
