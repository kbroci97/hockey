from sqlmodel import Session
from bioInstances import loadStatsFromCsv
from models import engine, Bio 

with Session(engine) as session:
    bios = loadStatsFromCsv("bio.csv")    
    for b in bios:
        session.add(b)
    session.commit()
