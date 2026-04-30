from typing import Optional

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class MessageManager:
    def __init__(self, state: FSMContext, chat_id: int, bot: Bot):
        self.state = state
        self.chat_id = chat_id
        self.bot = bot

    async def add_message(self, message: Message):
        data = await self.state.get_data()
        messages = data.get('bot_messages', [])
        messages.append(message.message_id)
        await self.state.update_data(bot_messages=messages)

    async def add_message_id(self, message_id: int):
        data = await self.state.get_data()
        messages = data.get('bot_messages', [])
        messages.append(message_id)
        await self.state.update_data(bot_messages=messages)

    async def delete_last(self) -> bool:
        data = await self.state.get_data()
        messages = data.get('bot_messages', [])

        if not messages:
            print("not messages")
            return False

        last_id = messages[-1]
        try:
            await self.bot.delete_message(self.chat_id, last_id)
            messages.pop()
            await self.state.update_data(bot_messages=messages)
            return True
        except Exception:
            print("catch exception")
            return False

    async def delete_all(self) -> int:
        data = await self.state.get_data()
        messages = data.get('bot_messages', [])

        deleted_count = 0
        for msg_id in messages:
            try:
                await self.bot.delete_message(self.chat_id, msg_id)
                deleted_count += 1
            except Exception:
                pass

        await self.state.update_data(bot_messages=[])
        return deleted_count

    async def delete_range(self, start: int, end: Optional[int] = None):
        data = await self.state.get_data()
        messages = data.get('bot_messages', [])

        if end is None:
            end = len(messages)

        to_delete = messages[start:end]
        for msg_id in to_delete:
            try:
                await self.bot.delete_message(self.chat_id, msg_id)
            except Exception:
                pass

        remaining = messages[:start] + messages[end:]
        await self.state.update_data(bot_messages=remaining)
