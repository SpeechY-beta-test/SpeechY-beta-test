from datetime import datetime
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserAnchor


class AnchorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_anchor(self, user_id: int) -> Optional[UserAnchor]:
        """
        :param user_id:
        :return:
        Anchor message from db
        """
        result = await self.session.execute(
            select(UserAnchor).where(UserAnchor.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def save_anchor(self, user_id: int, chat_id: int, message_id: int) -> UserAnchor:
        """
        Save, create and add anchor in db or update anchor
        :param user_id:
        :param chat_id:
        :param message_id:
        :return:
        Anchor message from db
        """
        anchor = await self.get_anchor(user_id)

        if anchor:
            anchor.chat_id = chat_id
            anchor.anchor_message_id = message_id
            anchor.updated_at = datetime.utcnow()
        else:
            anchor = UserAnchor(
                user_id=user_id,
                chat_id=chat_id,
                anchor_message_id=message_id,
            )
            self.session.add(anchor)
        await self.session.commit()
        await self.session.refresh(anchor)
        return anchor

    async def delete_anchor(self, user_id: int) -> bool:
        """
        delete anchor message from db
        :param user_id:
        :return:
        success_status
        """
        result = await self.session.execute(
            delete(UserAnchor).where(UserAnchor.user_id == user_id)
        )
        await self.session.commit()
        return True

