from sqlmodel import SQLModel, Field, create_engine
class Bio(SQLModel, table = True):
    firstName: str = Field(default = None, primary_key = True)
    lastName: str = Field(default = None, primary_key = True) 
    position: str | None = None
    jerseyNumber: int | None = None
    weight: int | None = None
    height: str | None = None
    classYear: str | None = None
    hometown: str | None = None
    highSchool: str | None = None

class Stats(SQLModel, table=True): 
    firstName: str = Field(primary_key=True, foreign_key="bio.firstName")
    lastName: str = Field(primary_key=True, foreign_key="bio.lastName")
    gp: int | None = None
    g: int | None = None
    a: int | None = None
    pts: int | None = None
    sh: int | None = None
    shPercent: float | None = None
    plusMinus: int | None = None
    ppg: int | None = None
    shg: int | None = None
    fg: int | None = None
    gwg: int | None = None
    gtg: int | None = None
    otg: int | None = None
    htg: int | None = None
    uag: int | None = None
    pnPim: str | None = None 
    min: int | None = None
    maj: int | None = None
    oth: int | None = None
    blk: int | None = None

engine = create_engine("sqlite:///hockey.db")
SQLModel.metadata.create_all(engine)
