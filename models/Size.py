from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from CrawlStarbucks.db.database import Base

# Bảng phụ cho mối quan hệ nhiều-nhiều giữa Drink và Size
# drink_size = Table(
#     'drink_size', Base.metadata,
#     Column('drink_id', Integer, ForeignKey('drink.id'), primary_key=True),
#     Column('size_id', Integer, ForeignKey('size.id'), primary_key=True),
#     extend_existing=True
# )

class Size(Base):
    __tablename__ = 'size'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    size_code = Column(String(50), unique=True, nullable=False)

    # Quan hệ với drink_info
    drink_infos = relationship("DrinkInfo", back_populates="size")
    # drinks = relationship('Drink', secondary=drink_size, back_populates='sizes')
