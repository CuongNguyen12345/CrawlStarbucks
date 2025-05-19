from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from CrawlStarbucks.db.database import Base

class Category(Base):
    __tablename__ = 'category'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('category.id'), nullable=True)

    # Quan hệ đệ quy
    parent = relationship('Category', remote_side=[id], backref=backref('children', cascade="all, delete"))

    drinks = relationship("Drink", back_populates="category", cascade="all, delete-orphan")