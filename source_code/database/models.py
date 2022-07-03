from sqlalchemy import String, Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Street(Base):
    __tablename__ = "streets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    street_id = Column(Integer, ForeignKey(Street.id, ondelete="cascade"))
    house = Column(Integer, nullable=False)
    frame = Column(String, nullable=False)
    flat = Column(Integer, nullable=False)
    full_name = Column(String, nullable=False)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    rate = Column(String, nullable=False)


class Accrual(Base):
    __tablename__ = "accruals"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey(Account.id, ondelete="cascade"))
    service_id = Column(Integer, ForeignKey(Service.id, ondelete="cascade"))
    quantity = Column(Integer, nullable=False)
