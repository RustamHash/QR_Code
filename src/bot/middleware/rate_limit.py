"""
Middleware для rate limiting.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

from ...core.exceptions import RateLimitError
from ...core.config import get_settings
from ...core.logging_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Класс для ограничения частоты запросов."""

    def __init__(self):
        self._requests: Dict[int, list[datetime]] = defaultdict(list)
        self._settings = get_settings()

    def check_rate_limit(self, user_id: int) -> Tuple[bool, int]:
        """
        Проверяет, не превышен ли лимит запросов.

        Args:
            user_id: ID пользователя

        Returns:
            Tuple[bool, int]: (разрешено ли, оставшееся время в секундах)

        Raises:
            RateLimitError: если лимит превышен
        """
        now = datetime.now()
        period = timedelta(seconds=self._settings.rate_limit_period)
        max_requests = self._settings.rate_limit_requests

        # Очищаем старые запросы
        self._requests[user_id] = [
            req_time for req_time in self._requests[user_id] if now - req_time < period
        ]

        # Проверяем лимит
        if len(self._requests[user_id]) >= max_requests:
            # Вычисляем время до следующего разрешенного запроса
            oldest_request = min(self._requests[user_id])
            wait_time = int((oldest_request + period - now).total_seconds())
            logger.warning(
                f"Rate limit превышен для пользователя {user_id}. " f"Ожидание: {wait_time} секунд"
            )
            raise RateLimitError(f"Превышен лимит запросов. Попробуйте через {wait_time} секунд.")

        # Добавляем текущий запрос
        self._requests[user_id].append(now)
        return True, 0

    def reset(self, user_id: int) -> None:
        """Сбрасывает счетчик запросов для пользователя."""
        self._requests[user_id] = []


# Глобальный экземпляр rate limiter
_rate_limiter = RateLimiter()


def check_rate_limit(user_id: int) -> None:
    """
    Проверяет rate limit для пользователя.

    Args:
        user_id: ID пользователя

    Raises:
        RateLimitError: если лимит превышен
    """
    _rate_limiter.check_rate_limit(user_id)
