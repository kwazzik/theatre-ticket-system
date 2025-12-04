from django.test import TestCase
from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import Play, TheatreHall, Performance, Ticket, Reservation
from app.serializers import TicketSerializer, ReservationSerializer, PlayImageSerializer
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta


class TicketSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("user@test.com", "pass123")
        self.hall = TheatreHall.objects.create(name="Main", rows=5, seats_in_row=5)
        self.play = Play.objects.create(title="Hamlet", description="Desc")
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.hall,
            show_time=datetime.now() + timedelta(days=1)
        )

    def test_ticket_validation_valid(self):
        data = {"row": 1, "seat": 1, "performance": self.performance}
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_ticket_validation_invalid_row(self):
        data = {"row": 6, "seat": 1, "performance": self.performance}
        serializer = TicketSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_ticket_validation_invalid_seat(self):
        data = {"row": 1, "seat": 6, "performance": self.performance}
        serializer = TicketSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class ReservationSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("user@test.com", "pass123")
        self.hall = TheatreHall.objects.create(name="Main", rows=5, seats_in_row=5)
        self.play = Play.objects.create(title="Hamlet", description="Desc")
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.hall,
            show_time=datetime.now() + timedelta(days=1)
        )

    def test_create_reservation_with_tickets(self):
        data = {
            "tickets": [
                {"row": 1, "seat": 1, "performance": self.performance},
                {"row": 2, "seat": 1, "performance": self.performance},
            ]
        }
        serializer = ReservationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save(user=self.user)

        self.assertEqual(reservation.tickets.count(), 2)
        self.assertEqual(reservation.tickets.first().reservation, reservation)


class PlayImageSerializerTests(TestCase):
    def test_upload_image(self):
        play = Play.objects.create(title="Hamlet", description="Desc")
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        serializer = PlayImageSerializer(play, data={"image": image})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        play.refresh_from_db()
        self.assertTrue(bool(play.image))
