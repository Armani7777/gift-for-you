from rest_framework import status
from rest_framework.test import APITestCase

from apps.invitations.models import Invitation
from apps.invitations.services import generate_management_token, generate_public_token


class InvitationAPITests(APITestCase):
    def setUp(self):
        self.payload = {
            "sender_name": "Arman",
            "recipient_name": "Anna",
            "main_message": "I have a little question for you...",
            "personal_message": "There are some things that are easier to say this way...",
            "theme": "elegant",
            "available_dates": ["2026-09-20", "2026-09-21", "2026-09-25"],
            "available_times": [{"time": "18:00"}, {"time": "19:00"}, {"time": "20:00"}],
            "activities": [
                {"name": "Coffee", "icon": "☕"},
                {"name": "Dinner", "icon": "🍝"},
            ],
        }

    def create_invitation(self, **overrides):
        payload = {**self.payload, **overrides}
        response = self.client.post("/api/invitations/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        return response.data

    def test_health(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_create_invitation_uses_random_tokens(self):
        data = self.create_invitation()
        invitation = Invitation.objects.get(public_token=data["public_token"])
        self.assertNotEqual(data["public_token"], str(invitation.id))
        self.assertNotEqual(data["public_token"], data["management_token"])
        self.assertEqual(len(data["public_token"]), 10)
        self.assertGreaterEqual(len(data["management_token"]), 32)

    def test_public_token_is_not_sequential(self):
        first = generate_public_token()
        second = generate_public_token()
        self.assertNotEqual(first, second)
        self.assertNotEqual(first, "1")

    def test_retrieve_invitation_hides_management_token(self):
        created = self.create_invitation()
        response = self.client.get(f"/api/invitations/{created['public_token']}/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("management_token", response.data)
        self.assertEqual(response.data["recipient_name"], "Anna")

    def test_invalid_token_returns_friendly_error(self):
        response = self.client.get("/api/invitations/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "This invitation is no longer available.")

    def test_open_marks_invitation_opened(self):
        created = self.create_invitation()
        response = self.client.post(f"/api/invitations/{created['public_token']}/open/")
        self.assertEqual(response.status_code, 200)
        invitation = Invitation.objects.get(public_token=created["public_token"])
        self.assertEqual(invitation.status, Invitation.Status.OPENED)
        self.assertIsNotNone(invitation.opened_at)

    def test_accept_and_confirm_flow(self):
        created = self.create_invitation()
        token = created["public_token"]
        public = self.client.get(f"/api/invitations/{token}/").data
        date_id = public["available_dates"][2]["id"]
        activity_id = public["activities"][1]["id"]

        response = self.client.post(f"/api/invitations/{token}/response/", {"answer": "accepted"}, format="json")
        self.assertEqual(response.status_code, 201)

        plan = self.client.post(
            f"/api/invitations/{token}/plan/",
            {"activity_ids": [activity_id], "date_id": date_id, "time": "19:00"},
            format="json",
        )
        self.assertEqual(plan.status_code, 200, plan.data)

        confirm = self.client.post(f"/api/invitations/{token}/confirm/")
        self.assertEqual(confirm.status_code, 200)
        invitation = Invitation.objects.get(public_token=token)
        self.assertEqual(invitation.status, Invitation.Status.CONFIRMED)
        self.assertEqual(invitation.response.selected_date.date.isoformat(), "2026-09-25")
        self.assertEqual(str(invitation.response.selected_time), "19:00:00")

    def test_duplicate_response_is_rejected(self):
        created = self.create_invitation()
        token = created["public_token"]
        first = self.client.post(f"/api/invitations/{token}/response/", {"answer": "declined"}, format="json")
        self.assertEqual(first.status_code, 201)
        second = self.client.post(f"/api/invitations/{token}/response/", {"answer": "accepted"}, format="json")
        self.assertEqual(second.status_code, 400)
        self.assertIn("already", second.data["error"].lower())
        self.assertEqual(Invitation.objects.get(public_token=token).status, Invitation.Status.DECLINED)

    def test_unavailable_date_is_rejected(self):
        created = self.create_invitation()
        token = created["public_token"]
        self.client.post(f"/api/invitations/{token}/response/", {"answer": "accepted"}, format="json")
        public = self.client.get(f"/api/invitations/{token}/").data
        plan = self.client.post(
            f"/api/invitations/{token}/plan/",
            {
                "activity_ids": [public["activities"][0]["id"]],
                "date_id": 999999,
                "time": "19:00",
            },
            format="json",
        )
        self.assertEqual(plan.status_code, 400)

    def test_unavailable_time_is_rejected(self):
        created = self.create_invitation()
        token = created["public_token"]
        self.client.post(f"/api/invitations/{token}/response/", {"answer": "accepted"}, format="json")
        public = self.client.get(f"/api/invitations/{token}/").data
        plan = self.client.post(
            f"/api/invitations/{token}/plan/",
            {
                "activity_ids": [public["activities"][0]["id"]],
                "date_id": public["available_dates"][0]["id"],
                "time": "03:00",
            },
            format="json",
        )
        self.assertEqual(plan.status_code, 400)
        self.assertIn("time", plan.data["error"].lower())

    def test_management_requires_matching_token(self):
        created = self.create_invitation()
        ok = self.client.get(f"/api/manage/{created['public_token']}/{created['management_token']}/")
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.data["status"], Invitation.Status.CREATED)

        forbidden = self.client.get(
            f"/api/manage/{created['public_token']}/{generate_management_token()}/"
        )
        self.assertEqual(forbidden.status_code, 403)

        public = self.client.get(f"/api/invitations/{created['public_token']}/")
        self.assertNotIn("management_token", public.data)
        self.assertNotIn("response", public.data)
