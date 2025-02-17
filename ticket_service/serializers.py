from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from theater_service.serializers import PlayListSerializer, TheaterHallSerializer
from ticket_service.models import Ticket, Reservation, Performance


class TicketSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            row=attrs["row"],
            seat=attrs["seat"],
            theater_hall=attrs["performance"].theater_hall,
            error_to_raise=ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "performance",
            "reservation",
        )


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at", "user")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        reservation = Reservation.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(reservation=reservation, **ticket_data)
        return reservation


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = (
            "id",
            "play",
            "theater_hall",
            "show_time",
        )


class PerformanceListSerializer(PerformanceSerializer):
    play_title = serializers.CharField(source="play.title", read_only=True)
    theater_hall_name = serializers.CharField(
        source="theater_hall.name", read_only=True
    )
    theater_hall_capacity = serializers.IntegerField(
        source="theater_hall.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Performance
        fields = (
            "id",
            "play_title",
            "theater_hall_name",
            "theater_hall_capacity",
            "show_time",
            "tickets_available",
        )


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlayListSerializer(many=False, read_only=True)
    theater_hall = TheaterHallSerializer(many=False, read_only=True)
    taken_seats = TicketSeatsSerializer(source="tickets", many=True, read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "show_time", "play", "theater_hall", "taken_seats")


class TicketListSerializer(TicketSerializer):
    performance = PerformanceListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
