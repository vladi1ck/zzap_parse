from django.contrib import messages
from django.core.cache import cache


class AdminNotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Показываем уведомления только в админке
        if request.path.startswith('/admin/'):

            cache_key = f"admin_notifications"
            notifications = cache.get(cache_key, [])

            for notification in notifications:
                messages.info(request, notification)

            # Очистка уведомлений после показа
            cache.delete(cache_key)

        response = self.get_response(request)
        return response
