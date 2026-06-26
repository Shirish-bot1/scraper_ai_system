from app.database.db import SessionLocal
from app.models.municipality import Municipality

def clean_database():
    db = SessionLocal()
    
    # This deletes rows where municipality_name is None or empty
    # This will remove that id=1 row you mentioned
    deleted_count = db.query(Municipality).filter(
        (Municipality.municipality_name == None) | 
        (Municipality.municipality_name == "")
    ).delete(synchronize_session=False)
    
    db.commit()
    db.close()
    
    print(f"Cleanup finished. Deleted {deleted_count} empty rows.")

if __name__ == "__main__":
    clean_database()