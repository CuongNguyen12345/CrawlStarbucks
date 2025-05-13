from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from Starbucks.db.database import Base
from Starbucks.models.Drink import drink_size

class Size(Base):
    __tablename__ = 'size'
    id = Column(Integer, primary_key=True, autoincrement=True)
    size_code = Column(String(50), unique=True, nullable=False)

    drinks = relationship('Drink', secondary=drink_size, back_populates='sizes')
