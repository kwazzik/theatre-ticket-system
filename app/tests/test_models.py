from django.test import TestCase
from django.core.exceptions import ValidationError
from app.models import Play, TheatreHall, Performance, Ticket
from django.contrib.auth import get_user_model


class PlayModelTests(TestCase):
    def test_play_str(self):
        play = Play.objects.create(title="Hamlet", description="Shakespeare play")
        self.assertEqual(str(play), play.title)

    def test_play_image_file_path(self):
        play = Play(title="Hamlet")
        filename = "myimage.jpg"
        path = play.image.field.upload_to(play, filename)
        self.assertIn("hamlet-", path)
        self.assertTrue(path.endswith(".jpg"))


class TheatreHallModelTests(TestCase):
    def test_capacity_property(self):
        hall = TheatreHall.objects.create(name="Main Hall", rows=5, seats_in_row=10)
        self.assertEqual(hall.capacity, 50)


class TicketModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="pass1234"
        )
        self.hall = TheatreHall.objects.create(name="Hall 1", rows=5, seats_in_row=5)
        self.play = Play.objects.create(title="Hamlet", description="Desc")
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.hall,
            show_time="2025-12-05T20:00:00Z"
        )
        self.reservation = self.user.reservations.create()

    def test_valid_ticket_save(self):
        ticket = Ticket(
            row=1,
            seat=1,
            performance=self.performance,
            reservation=self.reservation
        )
        ticket.save()
        self.assertTrue(Ticket.objects.filter(id=ticket.id).exists())

    def test_ticket_row_out_of_range_raises_validation_error(self):
        ticket = Ticket(
            row=6,
            seat=1,
            performance=self.performance,
            reservation=self.reservation
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_ticket_seat_out_of_range_raises_validation_error(self):
        ticket = Ticket(
            row=1,
            seat=6,
            performance=self.performance,
            reservation=self.reservation
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_ticket_unique_together_constraint(self):
        ticket1 = Ticket.objects.create(
            row=1,
            seat=1,
            performance=self.performance,
            reservation=self.reservation
        )
        ticket2 = Ticket(
            row=1,
            seat=1,
            performance=self.performance,
            reservation=self.reservation
        )
        with self.assertRaises(ValidationError):
            ticket2.full_clean()
