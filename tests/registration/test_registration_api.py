"""HTTP integration tests for provider registration."""

import os
import tempfile
import unittest

from functools import partial
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app
from backend.auth.database import initialize as initialize_auth
from backend.auth.sessions import create_session, get_session_email
from backend.registration.database import initialize
from backend.registration.profiles import get_profile, save_profile
from backend.registration.photo_storage import save_photo


class RegistrationAPITests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)

        self.auth_path = Path(temp.name) / "auth.db"
        self.path = Path(temp.name) / "registration.db"

        initialize_auth(self.auth_path)
        initialize(self.path)

        self.origin = "https://directory.example.com"
        self.email = "provider@example.invalid"
        self.headers = {"Origin": self.origin}

        patches = {
            "backend.api.registration.get_session_email":
                partial(get_session_email, database_path=self.auth_path),
            "backend.api.registration.get_profile":
                partial(get_profile, database_path=self.path),
            "backend.api.registration.save_profile":
                partial(save_profile, database_path=self.path),
            "backend.registration.photo_storage.save_photo":
                partial(save_photo, database_path=self.path),
            "backend.api.registration.find_existing_provider":
                lambda email: None,
        }

        for target, replacement in patches.items():
            mock = patch(target, replacement)
            mock.start()
            self.addCleanup(mock.stop)

        env = patch.dict(os.environ, {
            "AUTH_BASE_URL": self.origin,
            "AUTH_EMAIL_ENABLED": "0",
        })
        env.start()
        self.addCleanup(env.stop)

        self.client = TestClient(app, base_url=self.origin)
        self.addCleanup(self.client.close)

    def sign_in(self, email=None):
        token = create_session(
            email or self.email, self.auth_path
        )
        self.client.cookies.set("sv_session", token)

    def save(self, values):
        return self.client.patch(
            "/api/registration/profile",
            json=values,
            headers=self.headers,
        )

    def read(self):
        return self.client.get("/api/registration/profile")

    def upload(self, data):
        return self.client.put(
            "/api/registration/photo",
            content=data,
            headers=self.headers,
        )

    def test_unauthenticated_access(self):
        self.assertEqual(self.read().status_code, 401)
        self.assertEqual(self.save({}).status_code, 401)
        self.assertEqual(self.upload(b"image").status_code, 401)

    def test_new_profile(self):
        self.sign_in()
        self.assertIsNone(self.read().json()["profile"])

    def test_create_profile(self):
        self.sign_in()
        response = self.save({
            "first_name": "Test",
            "last_name": "Provider",
            "zip_code": "94506",
        })
        self.assertEqual(response.status_code, 200)
        profile = self.read().json()["profile"]
        self.assertEqual(profile["first_name"], "Test")
        self.assertEqual(profile["status"], "hidden")

    def test_edit_and_clear(self):
        self.sign_in()
        self.save({"first_name": "Original", "phone": "5550100"})
        response = self.save({"first_name": "Updated", "phone": None})
        self.assertEqual(response.status_code, 200)
        profile = self.read().json()["profile"]
        self.assertEqual(profile["first_name"], "Updated")
        self.assertIsNone(profile["phone"])

    def test_account_isolation(self):
        self.sign_in()
        self.save({"first_name": "First"})
        self.sign_in("other@example.invalid")
        self.assertIsNone(self.read().json()["profile"])
        self.save({"first_name": "Second"})
        self.sign_in()
        self.assertEqual(
            self.read().json()["profile"]["first_name"], "First"
        )

    def test_protected_fields(self):
        self.sign_in()
        for values in (
            {"status": "active"},
            {"account_email": "other@example.invalid"},
            {"terms_accepted": 1},
            {"profile_photo": "unvalidated"},
        ):
            self.assertEqual(self.save(values).status_code, 422)

    def test_origin_required(self):
        self.sign_in()
        response = self.client.patch(
            "/api/registration/profile",
            json={"first_name": "Test"},
        )
        self.assertEqual(response.status_code, 403)

    def test_travel_rates(self):
        self.sign_in()
        response = self.save({
            "price_per_mile": 725,
            "driving_hourly_rate": 50000,
            "charges_roundtrip_mileage": 1,
            "charges_roundtrip_driving_time": 0,
        })
        self.assertEqual(response.status_code, 200)
        profile = self.read().json()["profile"]
        self.assertEqual(profile["price_per_mile"], 725)
        self.assertEqual(profile["driving_hourly_rate"], 50000)
        self.assertEqual(profile["charges_roundtrip_mileage"], 1)
        self.assertEqual(profile["charges_roundtrip_driving_time"], 0)

    def test_invalid_rate(self):
        self.sign_in()
        self.assertEqual(
            self.save({"price_per_mile": -100}).status_code, 422
        )
        self.assertIsNone(self.read().json()["profile"])

    def test_photo_lifecycle(self):
        self.sign_in()
        self.save({"first_name": "Test"})

        photos = []

        for color in ("blue", "red"):
            buffer = BytesIO()
            Image.new("RGB", (800, 600), color).save(
                buffer, format="PNG"
            )

            response = self.upload(buffer.getvalue())
            self.assertEqual(response.status_code, 200)

            photo = response.json()["profile_photo"]
            self.assertTrue(photo.startswith("data:image/jpeg;base64,"))
            self.assertEqual(
                self.read().json()["profile"]["profile_photo"], photo
            )
            photos.append(photo)

        self.assertNotEqual(photos[0], photos[1])

        response = self.client.delete(
            "/api/registration/photo", headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(
            self.read().json()["profile"]["profile_photo"]
        )

    def test_invalid_photo(self):
        self.sign_in()
        self.save({"first_name": "Test"})
        self.assertEqual(self.upload(b"invalid").status_code, 422)

    def test_oversized_photo(self):
        self.sign_in()
        self.assertEqual(
            self.upload(b"x" * (5 * 1024 * 1024 + 1)).status_code,
            413,
        )


if __name__ == "__main__":
    unittest.main()
