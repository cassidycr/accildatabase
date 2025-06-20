# session_utils.py

from database import Session, InstructionSession
from sqlalchemy.orm import joinedload
from datetime import datetime, date
import pandas as pd

def parse_date(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None
    return None

def load_sessions():
    db_session = Session()
    sessions = db_session.query(InstructionSession).options(joinedload(InstructionSession.slos)).all()
    db_session.close()
    return sessions
