from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from Starbucks.db.database import Base


# Bảng trung gian giữa Drink và Size
drink_size = Table(
    'drink_size',
    Base.metadata,
    Column('drink_id', Integer, ForeignKey('drink.id'), primary_key=True),
    Column('size_id', Integer, ForeignKey('size.id'), primary_key=True)
)


class Drink(Base):
    __tablename__ = 'drink'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    display_order = Column(Integer)
    product_number = Column(Integer, unique=True)
    image_url = Column(String(500))

    category_id = Column(Integer, ForeignKey('category.id'), nullable=True)

    category = relationship("Category", back_populates="drinks")
    sizes = relationship('Size', secondary=drink_size, back_populates='drinks')