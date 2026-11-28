import hashlib
import unittest

from backend.auth.tokens import generate_token, hash_token


class TokenTests(unittest.TestCase):

    def test_token_length(self):
        self.assertEqual(len(generate_token()), 43)

    def test_token_url_safe(self):
        self.assertRegex(
            generate_token(),
            r"^[A-Za-z0-9_-]+$"
        )

    def test_tokens_are_unique(self):
        tokens = {generate_token() for _ in range(1000)}
        self.assertEqual(len(tokens), 1000)

    def test_hash_length(self):
        self.assertEqual(len(hash_token(generate_token())), 64)

    def test_hash_is_deterministic(self):
        token = generate_token()
        self.assertEqual(hash_token(token), hash_token(token))

    def test_hash_matches_sha256(self):
        expected = hashlib.sha256(b"example-token").hexdigest()
        self.assertEqual(hash_token("example-token"), expected)

    def test_different_tokens_have_different_hashes(self):
        self.assertNotEqual(
            hash_token(generate_token()),
            hash_token(generate_token())
        )


if __name__ == "__main__":
    unittest.main()
