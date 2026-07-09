import csv
from app.database.db import SessionLocal
from app.models.municipality import Municipality
from app.models.municipality_official import MunicipalityOfficial


def clean_row(row):
    """Remove None keys + strip headers safely"""
    return {
        str(k).strip(): v
        for k, v in row.items()
        if k is not None
    }


def safe_get(row, key):
    """Safely get value from CSV row"""
    return (row.get(key) or "").strip()


def import_officials_csv(csv_file_path):
    db = SessionLocal()

    with open(csv_file_path, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                row = clean_row(row)
                mun_name = safe_get(row, "Municipality")
                if not mun_name: continue

                
                mun = db.query(Municipality).filter(Municipality.municipality_name == mun_name).first()
                if not mun: continue

           
                official = db.query(MunicipalityOfficial).filter(MunicipalityOfficial.municipality_id == mun.id).first()

           
                def update_if_new(attr, new_val):
                    if new_val and new_val != getattr(official, attr):
                        setattr(official, attr, new_val)
                        return True
                    return False

                if official:
                  
                    updated = False
                    fields_to_check = {
                        "mayor_name": "Leader/Mayor Name",
                        "mayor_phone": "Leader/Mayor Phone",
                        "mayor_email": "Leader/Mayor Email",
                        "deputy_mayor_name": "Deputy Leader/Upa-Mayor Name",
                        "deputy_mayor_phone": "Deputy Leader/Upa-Mayor Phone",
                        "deputy_mayor_email": "Deputy Leader/Upa-Mayor Email"
                    }
                    
                    for db_attr, csv_key in fields_to_check.items():
                        if update_if_new(db_attr, safe_get(row, csv_key)):
                            updated = True
                    
                    if updated:
                        print(f"🔄 Updated: {mun_name}")
                    else:
                        print(f"✅ No changes needed: {mun_name}")

                else:
                  
                    official = MunicipalityOfficial(
                        municipality_id=mun.id,
                        province=safe_get(row, "Province"),
                        district=safe_get(row, "District"),
                        municipality_name=mun_name,
                        municipality_type=safe_get(row, "Type"),
                        website=safe_get(row, "Website"),
                        mayor_name=safe_get(row, "Leader/Mayor Name"),
                        mayor_phone=safe_get(row, "Leader/Mayor Phone"),
                        mayor_email=safe_get(row, "Leader/Mayor Email"),
                        deputy_mayor_name=safe_get(row, "Deputy Leader/Upa-Mayor Name"),
                        deputy_mayor_phone=safe_get(row, "Deputy Leader/Upa-Mayor Phone"),
                        deputy_mayor_email=safe_get(row, "Deputy Leader/Upa-Mayor Email"),
                    )
                    db.add(official)
                    print(f"🎉 Created new: {mun_name}")

            except Exception as e:
                print(f"❌ Error in row {mun_name}: {e}")

    db.commit()
    db.close()
    print(" IMPORT COMPLETED SUCCESSFULLY")

from pathlib import Path

if __name__ == "__main__":
    csv_path = Path(__file__).parent / "automations" / "municipality_official.csv"
    import_officials_csv(csv_path)