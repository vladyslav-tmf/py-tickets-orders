from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer

from cinema.models import Actor, CinemaHall, Genre, Movie, MovieSession, Order
from cinema.serializers import (
    ActorSerializer,
    CinemaHallSerializer,
    GenreSerializer,
    MovieDetailSerializer,
    MovieListSerializer,
    MovieSerializer,
    MovieSessionDetailSerializer,
    MovieSessionListSerializer,
    MovieSessionSerializer,
    OrderListSerializer,
    OrderSerializer
)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class CinemaHallViewSet(viewsets.ModelViewSet):
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()

    def get_serializer_class(self) -> Type[BaseSerializer]:
        if self.action == "list":
            return MovieListSerializer
        elif self.action == "retrieve":
            return MovieDetailSerializer

        return MovieSerializer


class MovieSessionViewSet(viewsets.ModelViewSet):
    queryset = MovieSession.objects.all()

    def get_serializer_class(self) -> Type[BaseSerializer]:
        if self.action == "list":
            return MovieSessionListSerializer
        elif self.action == "retrieve":
            return MovieSessionDetailSerializer

        return MovieSessionSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self) -> QuerySet[Order]:
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer: OrderSerializer) -> None:
        serializer.save(user=self.request.user)

    def get_serializer_class(self) -> Type[BaseSerializer]:
        if self.action == "list":
            return OrderListSerializer

        return super().get_serializer_class()
