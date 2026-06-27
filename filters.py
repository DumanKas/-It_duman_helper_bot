from functools import wraps
from aiogram.types import Message, CallbackQuery
from database import get_role

def admin_only(func):
    @wraps(func)
    async def wrapper(event, *args, **kwargs):  # event вместо message
        
        # определяем откуда берём user_id
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        role = get_role(user_id)
        if role != 'admin':
            if isinstance(event, Message):
                await event.answer("⛔ У вас нет доступа")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ У вас нет доступа", show_alert=True)
            return
        
        return await func(event, *args, **kwargs)
    
    return wrapper