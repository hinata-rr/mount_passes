import logging
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters, serializers
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import MountainPass, User
from .serializers import (
    MountainPassDetailSerializer,
    MountainPassCreateSerializer,
    MountainPassUpdateSerializer,
    MountainPassListSerializer,
    StatusUpdateSerializer,
)

logger = logging.getLogger(__name__)


class MountainPassViewSet(viewsets.ModelViewSet):
    """ViewSet для управления перевалами"""
    permission_classes = [AllowAny]
    queryset = MountainPass.objects.all().select_related(
        'user', 'coords', 'level'
    ).prefetch_related('images')

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return MountainPassCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return MountainPassUpdateSerializer
        elif self.action == 'list':
            return MountainPassListSerializer
        return MountainPassDetailSerializer

    def create(self, request, *args, **kwargs):
        """POST /submitData/ - создание нового перевала"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)

            logger.info(f"Создан новый перевал: {serializer.data.get('title')}")

            return Response(
                {
                    'status': 200,
                    'message': 'Отправлено успешно',
                    'id': serializer.instance.id
                },
                status=status.HTTP_200_OK,
                headers=headers
            )
        except serializers.ValidationError as e:
            logger.error(f"Ошибка валидации при создании перевала: {str(e)}")
            return Response(
                {
                    'status': 400,
                    'message': 'Ошибка валидации',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Ошибка при создании перевала: {str(e)}")
            return Response(
                {
                    'status': 500,
                    'message': 'Ошибка сервера',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """GET /submitData/<id>/ - получение перевала по ID"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response(
                {'error': 'Запись не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Ошибка при получении перевала: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """PATCH /submitData/<id>/ - редактирование перевала"""
        try:
            instance = self.get_object()

            if instance.status != 'new':
                return Response(
                    {
                        'state': 0,
                        'message': 'Редактирование возможно только для записей со статусом "new"'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            logger.info(f"Перевал {instance.id} обновлен")

            return Response(
                {
                    'state': 1,
                    'message': 'Запись успешно обновлена'
                },
                status=status.HTTP_200_OK
            )
        except serializers.ValidationError as e:
            return Response(
                {
                    'state': 0,
                    'message': 'Ошибка валидации',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Ошибка при обновлении перевала: {str(e)}")
            return Response(
                {
                    'state': 0,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        """PATCH /submitData/<id>/status/ - обновление статуса"""
        try:
            instance = self.get_object()
            serializer = StatusUpdateSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info(f"Статус перевала {instance.id} изменен на {instance.status}")

            return Response(
                {
                    'state': 1,
                    'message': 'Статус успешно обновлен'
                },
                status=status.HTTP_200_OK
            )
        except serializers.ValidationError as e:
            return Response(
                {
                    'state': 0,
                    'message': 'Ошибка валидации',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса: {str(e)}")
            return Response(
                {
                    'state': 0,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPassesListView(ListAPIView):
    """GET /submitData/?user__email=<email> - перевалы пользователя"""
    permission_classes = [AllowAny]
    serializer_class = MountainPassListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user__email']

    def get_queryset(self):
        email = self.request.query_params.get('user__email', None)
        if email:
            return MountainPass.objects.filter(
                user__email=email
            ).select_related('user', 'coords', 'level').order_by('-add_time')
        return MountainPass.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            email = request.query_params.get('user__email', None)
            if not email:
                return Response(
                    {'error': 'Не указан email пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Пользователь с указанным email не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )

            queryset = self.filter_queryset(self.get_queryset())

            if not queryset.exists():
                return Response(
                    {'count': 0, 'results': []},
                    status=status.HTTP_200_OK
                )

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)

            logger.info(f"Запрошены перевалы пользователя {email}")

            return Response({
                'count': len(serializer.data),
                'results': serializer.data
            })
        except Exception as e:
            logger.error(f"Ошибка при получении перевалов пользователя: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )