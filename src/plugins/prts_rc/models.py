from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class RCInfo(Model):
    __table_args__ = {"extend_existing": True}
    
    primary_key: Mapped[str] = mapped_column(String, primary_key=True)

    title: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    updated: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)

class SendMessage(Model):
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    primary_key: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    updated: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)