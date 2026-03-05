from sqlmodel import Session, select
from models import engine, Bio
from sqlalchemy import func
import pandas as pd 

with Session(engine) as session:
    statment = (
        select(Bio)
    )

    records = session.exec(statment).all()


recordsList = []
for record in records:
    recordsList.append(record.model_dump())

recorddf = pd.DataFrame(recordsList)
print(recorddf)
