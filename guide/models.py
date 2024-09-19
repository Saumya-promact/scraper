import datetime
from enum import Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import Enum as EnumType

# Create a base class for declarative class definitions
Base = declarative_base()


# Define the Enum for done_process column
class ProcessStatus(Enum):
    Scrapped = "Scrapped"
    Uploaded = "Uploaded"
    Content_extracted = "Content_extracted"
    Fact_extracted = "Fact_extracted"
    Metadata_extracted = "Metadata_extracted"
    Lexical_indexed = "Lexical_indexed"


# Define the DocumentProcessingRecord class representing the table
class DocumentProcessingRecord(Base):
    __tablename__ = "document_processing_log"

    id = Column(Integer, primary_key=True)
    pdf = Column(String, unique=True)
    pdf_link = Column(String)
    done_process = Column(EnumType(ProcessStatus), default=ProcessStatus.Scrapped)
    date = Column(Date)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    success_status = Column(Boolean, default=True)
    is_in_process = Column(Boolean, default=False)


class HighCourtJudges(Base):
    __tablename__ = "HighCourtJudges"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    code = Column(String, unique=True)
    court = Column(String)
    doj = Column(Date)
    held = Column(Date)
    scrapping_status = Column(String, default="Remaining")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
