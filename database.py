from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey, Boolean, Text  # type: ignore
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Connect to your database
engine = create_engine("sqlite:///acc_library_il.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define your main InstructionSession table
class InstructionSession(Base):
    __tablename__ = 'instruction_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_of_session = Column(Date)
    semester = Column(String)
    date_1 = Column(Date)
    date_2 = Column(Date)
    campus = Column(String)
    librarian_presenter = Column(String)
    co_librarian = Column(String)
    first = Column(String)
    last = Column(String)
    email = Column(String)
    course_code = Column(String)
    course_number = Column(String)
    time = Column(Time)  # New Time field
    length = Column(String)
    design_length = Column(String)
    type = Column(String)
    instruction_type = Column(String)
    campus_room = Column(String)
    day_of_week = Column(String)
    number_of_students = Column(Integer)
    assessment = Column(String)

    # New fields for cancellation
    canceled = Column(Boolean, default=False, nullable=False)
    canceled_reason = Column(Text, nullable=True)

    # Relationship to SLOs table
    slos = relationship("InstructionSessionSLO", back_populates="session", cascade="all, delete-orphan")

# Define the normalized SLO table
class InstructionSessionSLO(Base):
    __tablename__ = 'instruction_session_slos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('instruction_sessions.id'))
    slo = Column(String)

    # Relationship back to InstructionSession
    session = relationship("InstructionSession", back_populates="slos")

# Create tables if they don't exist
Base.metadata.create_all(engine)
