from sqlmodel import Session, select
from models import engine, Bio, Stats
from sqlalchemy import func
import pandas as pd 

with Session(engine) as session:
    statment = (
        select(Bio.position, func.avg(Bio.weight))
        .group_by(Bio.position)
        .having(func.avg(Bio.weight)>180)
    )
    records = session.exec(statment).all()


recorddf = pd.DataFrame(records)
print(recorddf)