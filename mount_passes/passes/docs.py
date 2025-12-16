"""
API Documentation for Mountain Passes Service

Base URL: /api/

Endpoints:
1. POST /api/submitData/
   - Создание нового перевала
   - Тело запроса: JSON с данными перевала
   - Ответ: {'status': 200, 'message': 'Отправлено успешно', 'id': <id>}

2. GET /api/submitData/<id>/
   - Получение перевала по ID
   - Ответ: Полные данные перевала

3. PATCH /api/submitData/<id>/
   - Редактирование перевала (только если status='new')
   - Тело запроса: JSON с изменяемыми полями
   - Ответ: {'state': 1, 'message': 'Запись успешно обновлена'}

4. GET /api/submitData/user_passes/?user__email=<email>
   - Получение всех перевалов пользователя
   - Ответ: Список перевалов с пагинацией

5. PATCH /api/submitData/<id>/status/
   - Обновление статуса перевала
   - Тело запроса: {'status': 'new|pending|accepted|rejected'}
   - Ответ: {'state': 1, 'message': 'Статус успешно обновлен'}

Пример запроса на создание:
{
  "beauty_title": "перевал",
  "title": "Северный",
  "other_titles": "Северный перевал",
  "connect": "Соединяет долины",
  "user": {
    "email": "test@example.com",
    "fam": "Иванов",
    "name": "Иван",
    "otc": "Иванович",
    "phone": "+79991234567"
  },
  "coords": {
    "latitude": 43.123456,
    "longitude": 42.654321,
    "height": 3500
  },
  "level": {
    "winter": "1A",
    "summer": "2A",
    "autumn": "1B",
    "spring": "1A"
  },
  "images": [
    {
      "title": "Вид с севера",
      "image": "base64_or_url"
    }
  ]
}
"""