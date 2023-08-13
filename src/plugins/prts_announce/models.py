from sqlalchemy import Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class ArkAnnounce(Model):
    __table_args__ = {"extend_existing": True}

    cid: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    category: Mapped[int] = mapped_column(Integer)
    displayTime: Mapped[str] = mapped_column(String)
    updatedAt: Mapped[int] = mapped_column(Integer)
    sticky: Mapped[bool] = mapped_column(Boolean)

class SendMessage(Model):
    __table_args__ = {"extend_existing": True}

    msgid: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    cid: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    category: Mapped[int] = mapped_column(Integer)
    displayTime: Mapped[int] = mapped_column(Integer)
    updatedAt: Mapped[str] = mapped_column(String)
    sticky: Mapped[bool] = mapped_column(Boolean)
    header: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    bannerImageUrl: Mapped[str] = mapped_column(String)