from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from app.models import Play, Genre, Actor, Performance, TheatreHall, Reservation, Ticket
from app.serializers import PlayListSerializer, PerformanceListSerializer, ReservationListSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime, timedelta

PLAY_URL = reverse("app:play-list")
PERFORMANCE_URL = reverse("app:performance-list")
RESERVATION_URL = reverse("app:reservation-list")

def detail_play_url(play_id):
    return reverse("app:play-detail", args=[play_id])

def upload_play_image_url(play_id):
    return reverse("app:play-upload-image", args=[play_id])

def sample_play(**params):
    defaults = {"title": "Sample Play", "description": "Description"}
    defaults.update(params)
    return Play.objects.create(**defaults)

def sample_genre(**params):
    defaults = {"name": "Action"}
    defaults.update(params)
    return Genre.objects.create(**defaults)

def sample_actor(**params):
    defaults = {"first_name": "John", "last_name": "Doe"}
    defaults.update(params)
    return Actor.objects.create(**defaults)

class PlayViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "pass123")
        self.admin = get_user_model().objects.create_user("admin@test.com", "pass123", is_staff=True)

    def test_filter_by_title(self):
        play1 = sample_play(title="Hamlet")
        sample_play(title="Macbeth")

        self.client.force_authenticate(self.user)
        res = self.client.get(PLAY_URL, {"title": "Hamlet"})
        serializer = PlayListSerializer(play1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data["results"])

    def test_filter_by_genres(self):
        play1 = sample_play(title="Action Play")
        play2 = sample_play(title="Comedy Play")
        genre1 = sample_genre(name="Action")
        genre2 = sample_genre(name="Comedy")
        play1.genres.add(genre1)
        play2.genres.add(genre2)

        self.client.force_authenticate(self.user)
        res = self.client.get(PLAY_URL, {"genres": f"{genre1.id},{genre2.id}"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_upload_image_admin_only(self):
        play = sample_play()
        url = upload_play_image_url(play.id)
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")

        # non-admin user
        self.client.force_authenticate(self.user)
        res = self.client.post(url, {"image": image}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # admin user
        self.client.force_authenticate(self.admin)
        res = self.client.post(url, {"image": image}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

class PerformanceViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "pass123")
        self.hall = TheatreHall.objects.create(name="Main", rows=5, seats_in_row=5)
        self.play = sample_play()
        self.perf1 = Performance.objects.create(
            play=self.play,
            theatre_hall=self.hall,
            show_time=datetime.now() + timedelta(days=1)
        )
        self.perf2 = Performance.objects.create(
            play=self.play,
            theatre_hall=self.hall,
            show_time=datetime.now() + timedelta(days=2)
        )

    def test_filter_by_date(self):
        date = (datetime.now() + timedelta(days=1)).date()
        self.client.force_authenticate(self.user)
        res = self.client.get(PERFORMANCE_URL, {"date": date})
        serializer = PerformanceListSerializer(self.perf1)
        self.assertIn(serializer.data, res.data["results"])

class ReservationViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "pass123")
        self.other_user = get_user_model().objects.create_user("other@test.com", "pass123")
        self.hall = TheatreHall.objects.create(name="Main", rows=5, seats_in_row=5)
        self.play = sample_play()
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.hall,
            show_time=datetime.now() + timedelta(days=1)
        )

    def test_queryset_returns_only_user_reservations(self):
        res_obj = Reservation.objects.create(user=self.user)
        Reservation.objects.create(user=self.other_user)
        Ticket.objects.create(row=1, seat=1, performance=self.performance, reservation=res_obj)

        self.client.force_authenticate(self.user)
        res = self.client.get(RESERVATION_URL)
        serializer = ReservationListSerializer(res_obj)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data["results"])
