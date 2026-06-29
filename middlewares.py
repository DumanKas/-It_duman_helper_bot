from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message,CallbackQuery
from database import get_role

class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        pool = data.get('pool')
        user = data.get('event_from_user')
        if user and pool:
            role = await get_role(pool, user.id)
            data['role'] = role
            if role == 'banned':
                if isinstance(event, Message):
                    await event.answer('❌ Вы заблокированы администрацией.')
                elif isinstance(event, CallbackQuery):
                    await event.answer('❌ Вы заблокированы.', show_alert=True)
                return
        return await handler(event, data)
        

