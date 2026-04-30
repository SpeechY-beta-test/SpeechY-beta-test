from aiogram import Router
from aiogram.types import Message

filter_router = Router()


@filter_router.message()
async def delete_delete_garbage_messages_handler(message: Message):
    await message.delete()
