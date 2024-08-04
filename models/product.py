from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://sujaypatel:password@localhost:5432/deal"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    retail = Column(Float)
    deal = Column(Float)
    saved = Column(String)
    description = Column(String)
    company = Column(String)
    clothing_type = Column(String)
    image = Column(String)
    external_link = Column(String)

def reset_table():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
