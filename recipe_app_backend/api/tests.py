from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class HealthTests(APITestCase):
    def test_health(self):
        url = reverse("Health")  # Make sure the URL is named
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})


class AuthAndRecipeTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="alice", password="Password123!")

    def test_register_and_login_and_recipe_crud_flow(self):
        # Register
        reg_resp = self.client.post(
            "/api/auth/register/",
            {"username": "bob", "password": "Password123!", "email": "bob@example.com"},
            format="json",
        )
        self.assertIn(reg_resp.status_code, (200, 201))
        self.assertIn("token", reg_resp.data)

        # Login
        login_resp = self.client.post(
            "/api/auth/login/", {"username": "alice", "password": "Password123!"}, format="json"
        )
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.data["token"]

        # Public list should work
        list_resp = self.client.get("/api/recipes/")
        self.assertEqual(list_resp.status_code, 200)

        # Create requires auth
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        create_resp = self.client.post(
            "/api/recipes/",
            {
                "title": "Pancakes",
                "description": "Fluffy pancakes",
                "ingredients": "Flour\nEggs\nMilk",
                "steps": "Mix\nCook",
                "image_url": "",
            },
            format="json",
        )
        self.assertIn(create_resp.status_code, (200, 201))
        rid = create_resp.data["id"]

        # Retrieve public
        retrieve_resp = self.client.get(f"/api/recipes/{rid}/")
        self.assertEqual(retrieve_resp.status_code, 200)
