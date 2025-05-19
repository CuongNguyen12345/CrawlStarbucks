from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from CrawlStarbucks.db.database import Base

class DrinkInfo(Base):
    __tablename__ = 'drink_info'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    drink_id = Column(Integer, ForeignKey('drink.id'), nullable=False)
    size_id = Column(Integer, ForeignKey('size.id'), nullable=False)
    ingredients = Column(String(500), nullable=True)  # Cho phép NULL vì có thể không có thông tin ingredients
    calories = Column(Integer, nullable=True)         # Có thể không có thông tin calories
    total_fat = Column(Integer, nullable=True)
    saturated_fat = Column(Integer, nullable=True)
    trans_fat = Column(Integer, nullable=True)
    cholesterol = Column(Integer, nullable=True)
    sodium = Column(Integer, nullable=True)
    total_carbs = Column(Integer, nullable=True)
    dietary_fiber = Column(Integer, nullable=True)
    sugars = Column(Integer, nullable=True)
    protein = Column(Integer, nullable=True)
    caffeine = Column(Integer, nullable=True)

    # Thiết lập quan hệ ngược lại
    drink = relationship("Drink", back_populates="drink_infos")
    size = relationship("Size", back_populates="drink_infos")