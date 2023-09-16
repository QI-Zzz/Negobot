# from . import db
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, Integer
from typing import List



class Base(DeclarativeBase):
    pass



class Conversation(Base):
    __tablename__ = 'conversation'
    user_id: Mapped[int] = mapped_column (primary_key=True)
    order_turn: Mapped[int] = mapped_column(primary_key =True)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    utterance: Mapped[str] = mapped_column(Text, nullable=False)
    
    # user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable = False)
    # text: Mapped[str] = mapped_column(Text, nullable=False)
    # user: Mapped['User'] = relationship(back_populates='conversation')



class Question(Base):
    __tablename__ = 'Questions'
    user_id: Mapped[int] = mapped_column (primary_key=True)
    Q1: Mapped[int] = mapped_column(Integer, nullable=False)
    Q2: Mapped[int] = mapped_column(Integer, nullable=False)
    Q3: Mapped[int] = mapped_column(Integer, nullable=False)
    Q4: Mapped[int] = mapped_column(Integer, nullable=False)
    Q5: Mapped[int] = mapped_column(Integer, nullable=False)
    Q6: Mapped[int] = mapped_column(Integer, nullable=False)
    # conversation: Mapped[List['Conversation',]] = relationship(back_populates='user')
