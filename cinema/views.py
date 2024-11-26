from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer

from cinema.models import Actor, CinemaHall, Genre, Movie, MovieSession, Order
from cinema.pagination import OrderViewSetPagination
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

    @staticmethod
    def _params_to_int(query_string) -> list[int]:
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self) -> QuerySet[Movie]:
        queryset = super().get_queryset()

        if self.action == "list":
            actors = self.request.query_params.get("actors")
            genres = self.request.query_params.get("genres")
            title = self.request.query_params.get("title")

            if actors:
                actors_ids = self._params_to_int(actors)
                queryset = queryset.filter(actors__id__in=actors_ids)

            if genres:
                queryset = queryset.filter(genres__name__icontains=genres)

            if title:
                queryset = queryset.filter(title__icontains=title)

        return queryset

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
    pagination_class = OrderViewSetPagination

    def get_queryset(self) -> QuerySet[Order]:
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer: OrderSerializer) -> None:
        serializer.save(user=self.request.user)

    def get_serializer_class(self) -> Type[BaseSerializer]:
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer
