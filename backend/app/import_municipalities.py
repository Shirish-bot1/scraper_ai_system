
# import csv
# from app.database.db import SessionLocal
# # Make sure to import the Class Name (Municipality), not the module
# from app.models.municipality import Municipality
# def import_csv_to_db(csv_file_path):
#     db = SessionLocal()
    
#     # Open the CSV file
#     with open(csv_file_path, mode='r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
        
#         for row in reader:
#             # Use the Class 'Municipality' here
#             exists = db.query(Municipality).filter_by(municipality_name=row['municipality']).first()
            
#             if not exists:
#                 # Use the Class 'Municipality' to create a new record
#                 new_m = Municipality(
#                     province=row['province'],
#                     district=row['district'],
#                     municipality_name=row['municipality'],
#                     municipality_type=row['type'],
#                     website=row['website'],
#                     email=row['email'],
#                     phone=row['phone']
#                 )
#                 db.add(new_m)
#                 print(f"Added: {row['municipality']}")
#             else:
#                 print(f"Skipped (Already exists): {row['municipality']}")
                
#     db.commit()
#     db.close()
#     print("Import completed successfully!")
# from pathlib import Path

# if __name__ == "__main__":
#     csv_path = Path(__file__).parent / "automations" / "municipalities.csv"
#     import_csv_to_db(csv_path)

import csv
from pathlib import Path

from app.database.db import SessionLocal
from app.models.municipality import Municipality


def import_csv_to_db(csv_file_path):
    db = SessionLocal()

    # Read all rows from CSV
    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # ===============================
    # Delete municipalities removed from CSV
    # ===============================
    csv_names = {row["municipality"].strip() for row in rows}

    db_municipalities = db.query(Municipality).all()

    for municipality in db_municipalities:
        if municipality.municipality_name not in csv_names:
            print(f"🗑 Deleting: {municipality.municipality_name}")
            db.delete(municipality)

    db.commit()

    # ===============================
    # Insert or Update municipalities
    # ===============================
    for row in rows:

        municipality = db.query(Municipality).filter_by(
            municipality_name=row["municipality"].strip()
        ).first()

        if municipality:
            municipality.province = row["province"]
            municipality.district = row["district"]
            municipality.municipality_type = row["type"]
            municipality.website = row["website"]
            municipality.email = row["email"]
            municipality.phone = row["phone"]

            print(f"🔄 Updated: {row['municipality']}")

        else:
            new_municipality = Municipality(
                province=row["province"],
                district=row["district"],
                municipality_name=row["municipality"],
                municipality_type=row["type"],
                website=row["website"],
                email=row["email"],
                phone=row["phone"],
            )

            db.add(new_municipality)

            print(f"➕ Added: {row['municipality']}")

    db.commit()
    db.close()

    print("🎉 Municipality import completed successfully!")


if __name__ == "__main__":
    csv_path = Path(__file__).parent / "automations" / "municipalities.csv"
    import_csv_to_db(csv_path)