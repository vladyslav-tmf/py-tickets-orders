from django.db import transaction
from rest_framework import serializers

from cinema.models import (
    Actor,
    CinemaHall,
    Genre,
    Movie,
    MovieSession,
    Order,
    Ticket
)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ["id", "first_name", "last_name", "full_name"]


class CinemaHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinemaHall
        fields = ["id", "name", "rows", "seats_in_row", "capacity"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "description", "duration", "genres", "actors"]


class MovieListSerializer(MovieSerializer):
    genres = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    actors = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )


class MovieDetailSerializer(MovieSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "description", "duration", "genres", "actors"]


class MovieSessionSerializer(serializers.ModelSerializer):
    movie_title = serializers.SlugRelatedField(
        source="movie", read_only=True, slug_field="title"
    )
    cinema_hall_name = serializers.SlugRelatedField(
        source="cinema_hall", read_only=True, slug_field="name"
    )
    cinema_hall_capacity = serializers.SlugRelatedField(
        source="cinema_hall", read_only=True, slug_field="capacity"
    )

    class Meta:
        model = MovieSession
        fields = [
            "id",
            "show_time",
            "movie_title",
            "cinema_hall_name",
            "cinema_hall_capacity"
        ]


class MovieSessionListSerializer(MovieSessionSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    cinema_hall_name = serializers.CharField(
        source="cinema_hall.name", read_only=True
    )
    cinema_hall_capacity = serializers.IntegerField(
        source="cinema_hall.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField()

    class Meta:
        model = MovieSession
        fields = [
            "id",
            "show_time",
            "movie_title",
            "cinema_hall_name",
            "cinema_hall_capacity",
            "tickets_available"
        ]


class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["row", "seat"]


class MovieSessionDetailSerializer(MovieSessionSerializer):
    movie = MovieListSerializer(read_only=True)
    cinema_hall = CinemaHallSerializer(read_only=True)
    taken_places = TicketListSerializer(
        many=True, source="tickets",read_only=True
    )

    class Meta:
        model = MovieSession
        fields = ["id", "show_time", "movie", "cinema_hall", "taken_places"]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "movie_session"]

    def validate(self, attrs: dict) -> dict:
        movie_session = attrs.get("movie_session")
        row = attrs.get("row")
        seat = attrs.get("seat")

        if not (1 <= row <= movie_session.cinema_hall.rows):
            raise serializers.ValidationError(
                {
                    "row": (
                        "Row number must be in range: "
                        f"(1, {movie_session.cinema_hall.rows})."
                    )
                }
            )

        if not (1 <= seat <= movie_session.cinema_hall.seats_in_row):
            raise serializers.ValidationError(
                {
                    "seat": (
                        "Seat number must be in range: "
                        f"(1, {movie_session.cinema_hall.seats_in_row})."
                    )
                }
            )

        if Ticket.objects.filter(
                movie_session=movie_session, row=row, seat=seat
        ).exists():
            raise serializers.ValidationError(
                f"Seat {seat} in row {row} is already taken."
            )

        return attrs


class TicketDetailSerializer(TicketSerializer):
    movie_session = MovieSessionSerializer()


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "tickets", "created_at"]

    def create(self, validated_data: dict) -> Order:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)

            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)

            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True)
