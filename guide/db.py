import os
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models import DocumentProcessingRecord, ProcessStatus, HighCourtJudges

load_dotenv()

# Create a PostgreSQL database engine
engine = create_engine(
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
)


# Create a function to add error records
def add_record(pdf_link):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        pdf = pdf_link.split("/")[-1]
        record = DocumentProcessingRecord(
            pdf=pdf,
            pdf_link=pdf_link,
            date=datetime.date.today(),
        )
        session.add(record)
        session.commit()
    except IntegrityError:
        # Handle the unique constraint violation exception
        session.rollback()  # Roll back the transaction
        print("Duplicate PDF name detected.")
    except Exception as e:
        # Handle other exceptions
        session.rollback()  # Roll back the transaction
        print(f"Error in adding record - {e}")
    finally:
        session.close()


# Add Hc Record
def add_hc_record(pdf):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        record = DocumentProcessingRecord(
            pdf=pdf,
            pdf_link="",
            done_process=ProcessStatus.Uploaded,
            date=datetime.date.today(),
        )
        session.add(record)
        session.commit()
        print("added")
    except IntegrityError:
        # Handle the unique constraint violation exception
        session.rollback()  # Roll back the transaction
        print("Duplicate PDF name detected.")
    except Exception as e:
        # Handle other exceptions
        session.rollback()  # Roll back the transaction
        print(f"Error in adding record - {e}")
    finally:
        session.close()


# Get scrapped records
def get_scrapped_records():
    try:
        # Create a session to interact with the database
        Session = sessionmaker(bind=engine)
        session = Session()

        # Fetch the record where process is equal to the specified name
        records = (
            session.query(DocumentProcessingRecord.pdf_link)
            .filter_by(done_process=ProcessStatus.Scrapped)
            .all()
        )

        # Check if the record is found and return id and remaining_pdfs
        if records:
            session.close()
            return [record.pdf_link for record in records]
    except Exception as e:
        session.close()
        print(f"Error in getting records {e}")
        return False


# Update the records
def update_record_process(pdf_link, success=True):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        record_to_update = (
            session.query(DocumentProcessingRecord).filter_by(pdf_link=pdf_link).first()
        )

        if record_to_update:
            # Update the done_process field to the specified next_process
            record_to_update.done_process = ProcessStatus.Uploaded
            record_to_update.success_status = success

            # Commit the changes
            session.commit()
            print("Db update")
        else:
            print("No record in db")
    except Exception as e:
        print(f"Error in updating record {e}")
    finally:
        # Close the session
        session.close()


# Update bombay records
def update_bombay_hc_record_process(pdf_link, pdf, success=True):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        record_to_update = (
            session.query(DocumentProcessingRecord).filter_by(pdf_link=pdf_link).first()
        )

        if record_to_update:
            # Update the done_process field to the specified next_process
            record_to_update.done_process = ProcessStatus.Uploaded
            record_to_update.success_status = success

            # Set the pdf column
            record_to_update.pdf = pdf

            # Commit the changes
            session.commit()
            print("Db update")
        else:
            print("No record in db")
    except Exception as e:
        print(f"Error in updating record {e}")
    finally:
        # Close the session
        session.close()


# Add judges and their unique codes
def add_judge(judge, code, court, doj=None, held=None):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # Convert date strings to datetime objects
        doj_date = datetime.datetime.strptime(doj, "%d/%m/%Y") if doj else None
        held_date = datetime.datetime.strptime(held, "%d/%m/%Y") if held else None

        record = HighCourtJudges(
            name=judge, code=code, court=court, doj=doj_date, held=held_date
        )
        session.add(record)
        session.commit()
        print(f"Added {judge} from {court}")
    except IntegrityError:
        # Handle the unique constraint violation exception
        session.rollback()  # Roll back the transaction
        print("Duplicate Judge name detected.")
    except Exception as e:
        # Handle other exceptions
        session.rollback()  # Roll back the transaction
        print(f"Error in adding judge - {e}")
    finally:
        session.close()


# Get judge
def get_judge():
    try:
        Session = sessionmaker(bind=engine)
        with Session() as session:
            record = (
                session.query(HighCourtJudges)
                .filter_by(scrapping_status="Remaining")
                .order_by(HighCourtJudges.name)
                .first()
            )

            if record:
                judge = record
                record.scrapping_status = "In Progress"
                session.commit()
                print(f"{judge.name} is in progress")
                return judge
            else:
                print("Completed for all judges")
    except Exception as e:
        print(e)


# Get list of judges
def get_all_judges():
    try:
        Session = sessionmaker(bind=engine)
        with Session() as session:
            record = session.query(HighCourtJudges).all()
            if record:
                return record
    except Exception:
        session.close()


# Update judges details
def update_judge_doj(judge, doj, held):
    try:
        Session = sessionmaker(bind=engine)
        with Session() as session:
            record_to_update = (
                session.query(HighCourtJudges).filter_by(name=judge).first()
            )

            # Convert date strings to datetime objects
            doj_date = datetime.datetime.strptime(doj, "%d/%m/%Y") if doj else None
            held_date = datetime.datetime.strptime(held, "%d/%m/%Y") if held else None

            if record_to_update:
                record_to_update.doj = doj_date
                record_to_update.held = held_date

                session.commit()
                print(f"Doj added for {judge}")
            else:
                print("No record in db")
    except Exception as e:
        # Handle other exceptions
        print(f"Error in adding judge - {e}")


# Update judge scrapping status
def update_judge_status(judge, status="Completed"):
    try:
        Session = sessionmaker(bind=engine)
        with Session() as session:
            record_to_update = (
                session.query(HighCourtJudges).filter_by(name=judge).first()
            )

            if record_to_update:
                record_to_update.scrapping_status = status
                session.commit()
                print(f"Scrapping for {judge} is {status}")
    except Exception as e:
        print(e)


# Delete judges without doj
def delete_judges_without_doj():
    try:
        Session = sessionmaker(bind=engine)
        with Session() as session:
            # Delete records with done_process of Lexical_indexed
            session.query(HighCourtJudges).filter_by(doj=None).delete()

            # Commit the changes
            session.commit()
            print("Deleted Judges without DoJ")
    except Exception as e:
        print(f"Error in record deletion {e}")
