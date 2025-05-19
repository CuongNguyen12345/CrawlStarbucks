from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from CrawlStarbucks.db.database import Base
# from CrawlStarbucks.models.Size import drink_size

class Drink(Base):
    __tablename__ = 'drink'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    display_order = Column(Integer)
    form_code = Column(String(50))
    product_number = Column(Integer)
    image_url = Column(String(500))

    category_id = Column(Integer, ForeignKey('category.id'), nullable=True)

    category = relationship("Category", back_populates="drinks")
    # Quan hệ với drink_info
    drink_infos = relationship("DrinkInfo", back_populates="drink")

    # sizes = relationship('Size', secondary=drink_size, back_populates='drinks')