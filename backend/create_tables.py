from db import engine
from models.price import Base
from models.indicator import Indicator

Base.metadata.create_all(engine)
print("Tables created successfully.")

