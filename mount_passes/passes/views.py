from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import MountainPass
from .serializers import MountainPassSerializer, MountainPassUpdateSerializer
import logging

logger = logging.getLogger(__name__)


class SubmitDataView(APIView):
    """API endpoint для добавления данных о перевале"""
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = MountainPassSerializer(data=request.data)
            if serializer.is_valid():
                mountain_pass = serializer.save()

                # Логируем успешное добавление
                logger.info(f"Новый перевал добавлен: {mountain_pass.title} (ID: {mountain_pass.id})")

                # Возвращаем успешный ответ
                return Response({
                    'status': 200,
                    'message': 'Отправлено успешно',
                    'id': mountain_pass.id
                }, status=status.HTTP_200_OK)

            # Возвращаем ошибки валидации
            return Response({
                'status': 400,
                'message': 'Некорректный запрос',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Ошибка при добавлении перевала: {str(e)}")
            return Response({
                'status': 500,
                'message': 'Ошибка сервера',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_pass_by_id(request, pk):
    """Получение перевала по ID"""
    try:
        mountain_pass = get_object_or_404(MountainPass, pk=pk)
        serializer = MountainPassSerializer(mountain_pass)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_pass_status(request, pk):
    """Обновление статуса перевала (для модераторов)"""
    try:
        mountain_pass = get_object_or_404(MountainPass, pk=pk)
        serializer = MountainPassUpdateSerializer(mountain_pass, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'state': 1,
                'message': 'Статус успешно обновлен'
            })
        return Response({
            'state': 0,
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'state': 0,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)