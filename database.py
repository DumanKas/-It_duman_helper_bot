import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

async def create_tables(pool):
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                name TEXT,
                description TEXT,
                price INTEGER
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                service_id INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        ''')

async def add_user(pool, user_id: int, username: str):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users(id, username)
            VALUES($1, $2)
            ON CONFLICT DO NOTHING
        ''', user_id, username)

async def get_role(pool, user_id: int) -> str:
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            'SELECT role FROM users WHERE id = $1', user_id
        )
    if result is None:
        return 'user'
    return result['role']

async def set_role(pool, user_id: int, role: str):
    async with pool.acquire() as conn:
        await conn.execute(
            'UPDATE users SET role = $1 WHERE id = $2', role, user_id
        )

async def get_all_users(pool):
    async with pool.acquire() as conn:
        return await conn.fetch('SELECT * FROM users')

async def add_service(pool, name: str, description: str, price: int):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO services(name, description, price)
            VALUES($1, $2, $3)
        ''', name, description, price)

async def get_services(pool):
    async with pool.acquire() as conn:
        return await conn.fetch('SELECT * FROM services')

async def get_service(pool, service_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            'SELECT * FROM services WHERE id = $1', service_id
        )

async def delete_service(pool, service_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            'DELETE FROM services WHERE id = $1', service_id
        )

async def add_order(pool, user_id: int, service_id: int, date: str):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO orders(user_id, service_id, date)
            VALUES($1, $2, $3)
        ''', user_id, service_id, date)

async def get_all_orders(pool):
    async with pool.acquire() as conn:
        return await conn.fetch('SELECT * FROM orders')
    