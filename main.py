import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_all_orders,get_all_users,get_order,set_role,get_role,get_service,get_services,add_order,add_service,add_user,delete_order,create_pool,delete_service,create_tables
from datetime import datetime
from filters import admin_only
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from middlewares import RoleMiddleware
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncpg


ADMIN_IDS = [834966781]  

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
BOT_TOKEN = os.getenv('BOT_TOKEN')
dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)


class DeleteService(StatesGroup):
    service_id = State()
class Add_Service(StatesGroup):
    name = State()
    description = State()
    price = State()

@dp.message(Command('start'))
async def start_command(message: Message,pool: None):
    user_id = message.from_user.id
    username = message.from_user.username
    await add_user(pool, user_id, username)
    if user_id in ADMIN_IDS:
        await set_role(pool, user_id, 'admin')

    await message.answer("Добро пожаловать!")

@dp.message(Command('services'))
async def services_command(message: Message,pool: None):
    services = await get_services(pool)
    if not services:
        await message.answer("📋 Список услуг пуст.")
        return
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.button(text=f"{service[1]} - {service[3]} тг",
                       callback_data=f"order_{service[0]}")
        
    builder.adjust(1)
    await message.answer('📋 Выберите услугу:', reply_markup=builder.as_markup())
    

@dp.callback_query(F.data.startswith("order_"))
async def order_command(callback: types.CallbackQuery,pool: None):
    service_id = int(callback.data.split("_")[1])
    service =   await get_service(pool, service_id)
    if service is None:
        await callback.answer('❌ Услуга не найдена')
        await callback.answer()
        return
    
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    await add_order(pool,callback.from_user.id,service_id,date)
    await callback.message.answer(f"✅ Заявка на {service[1]} принята!\nМы свяжемся с вами")
    await callback.answer()

@dp.message(Command('admin'))
@admin_only
async def admin_command(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text='add',callback_data='add')
    builder.button(text='delete <id>',callback_data='delete')
    builder.button(text='📋 Все заказы',callback_data='orders')
    builder.adjust(1)
    await message.answer("👑 Панель админа", reply_markup=builder.as_markup())



@dp.callback_query(F.data == 'add')
@admin_only
async def admin_add(callback: types.CallbackQuery, state:FSMContext,):
    await callback.message.answer("Введите название услуги: ")
    await state.set_state(Add_Service.name)
    await callback.answer()


@dp.message(Add_Service.name)
async def add_name(message: Message, state:FSMContext):
    await state.update_data(name = message.text)
    await message.answer("Введите описание: ")
    await state.set_state(Add_Service.description)


@dp.message(Add_Service.description)
async def add_description(message: Message, state:FSMContext):
    await state.update_data(description = message.text)
    await message.answer("Введите цену")
    await state.set_state(Add_Service.price)


@dp.message(Add_Service.price)
async def add_price(message: Message, state: FSMContext, pool: None):
    data = await state.get_data()
    await add_service(pool, name = data['name'],
                description=data['description'],
                price = int(message.text))
    
    await message.answer(f"✅ Услуга '{data['name']}' добавлена!")
    await state.clear()

@dp.callback_query(F.data == 'delete')
@admin_only
async def delete_command(callback: types.CallbackQuery, state: FSMContext,pool: None):
    services = await get_services(pool)
    if not services:
        await callback.message.answer("Услуг нет")
        await callback.answer()
        return
    
    text = "Список услуг"
    for service in services:
        text += f"{service[0]}. {service[1]} - {service[3]} тг\n"
    text += "\nВведите id услуги которую хотите удалить:"
    await callback.message.answer(text)
    await state.set_state(DeleteService.service_id)
    await callback.answer()


@dp.message(DeleteService.service_id)
async def confirm_delete(message: Message, state: FSMContext,pool: None):
    service_id = int(message.text) 
    service = await get_service(pool, service_id)

    if service is None:
        await message.answer("❌ Услуги с таким id нет")
        await state.clear()
        return
    await delete_service(pool, service_id)
    await message.answer('Услуга удалена')
    await state.clear()


@dp.callback_query(F.data == 'orders')
@admin_only
async def admin_order_command(callback: types.CallbackQuery, pool: None):
    orders = await get_all_orders(pool)

    if not orders:
        await callback.message.answer("Заказов нет")
        await callback.answer()
        return
    
    text = "📋 Все заказы:\n\n"

    for order in orders:
        text += f"🔹 Заказ #{order[0]}\n"
        text += f"🔹 Юзер #{order[1]}\n"
        text += f"🔹 Услуга #{order[2]}\n"
        text += f"🔹 Дата #{order[3]}\n"

    await callback.message.answer(text)
    await callback.answer()


async def main():
    pool = await create_pool()
    dp['pool'] = pool
    await create_tables(pool)


    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(RoleMiddleware())
    await bot.set_my_commands([
        BotCommand(command= 'start', description = "Запуск"),
        BotCommand(command = 'services', description = "список всех услуг с ценами"),
        BotCommand(command = 'order',description = 'оставить заявку на услугу'),
        BotCommand(command='add', description='добавить услугу(Для админа)'),
        BotCommand(command='delete', description='удалить услугу'),
        BotCommand(command='orders', description='посмотреть все заявки')
    ])
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    app = web.Application()
    SimpleRequestHandler(dispatcher = dp, bot = bot).register(app, path='/webhook')
    setup_application(app, dp, bot = bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
    await site.start()



if __name__ == '__main__':
    asyncio.run(main())