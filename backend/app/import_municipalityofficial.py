import csv
from app.database.db import SessionLocal
from app.models.municipality import Municipality
from app.models.municipality_official import MunicipalityOfficial


# -----------------------------
# SAFE CSV CLEANING
# -----------------------------
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


# -----------------------------
# MAIN IMPORT FUNCTION
# -----------------------------
def import_officials_csv(csv_file_path):
    db = SessionLocal()

    with open(csv_file_path, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                row = clean_row(row)
                mun_name = safe_get(row, "Municipality")
                if not mun_name: continue

                # 1. Find Municipality
                mun = db.query(Municipality).filter(Municipality.municipality_name == mun_name).first()
                if not mun: continue

                # 2. Get existing official record or create a new one
                official = db.query(MunicipalityOfficial).filter(MunicipalityOfficial.municipality_id == mun.id).first()

                # Helper to update fields ONLY if new value exists and is different
                def update_if_new(attr, new_val):
                    if new_val and new_val != getattr(official, attr):
                        setattr(official, attr, new_val)
                        return True
                    return False

                if official:
                    # UPDATING EXISTING RECORD
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
                    # CREATING NEW RECORD
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
    print("🎉 IMPORT COMPLETED SUCCESSFULLY")


# -----------------------------
# RUN SCRIPT
# -----------------------------
if __name__ == "__main__":
    import_officials_csv(r"C:\Users\shiri\scraper_ai_system\backend\app\automations\municipality_official.csv")