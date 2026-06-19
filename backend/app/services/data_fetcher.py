from collections import defaultdict
from app.database.db import SessionLocal
from app.models.municipality import Municipality
from app.models.municipality_official import MunicipalityOfficial
import pandas as pd

def get_complete_municipality_data(name: str):
    """
    Fetches detailed info and officials for a specific municipality.
    """
    db = SessionLocal()
    try:
        # Search by name with partial match
        search_query = f"%{name.strip()}%"
        mun = db.query(Municipality).filter(Municipality.municipality_name.ilike(search_query)).first()
        
        if not mun:
            return None
        
        officials = db.query(MunicipalityOfficial).filter(
            MunicipalityOfficial.municipality_id == mun.id
        ).all()
        
        return {
            "municipality_info": {
                "name": mun.municipality_name,
                "district": mun.district,
                "province": mun.province,
                "website": mun.website,
                "phone": getattr(mun, 'phone', None)
            },
            "officials": [{
                "mayor": o.mayor_name, 
                "mayor_email": o.mayor_email, 
                "mayor_phone": o.mayor_phone, 
                "deputy": o.deputy_mayor_name,
                "deputy_phone": o.deputy_mayor_phone,
                "deputy_email": o.deputy_mayor_email
            } for o in officials]
        }
    except Exception as e:
        print(f"Error fetching specific municipality: {e}")
        return None
    finally:
        db.close()

def get_full_database_dump():
    """
    Fetches all municipalities and maps officials to them.
    Added a limit to prevent browser hanging.
    """
    db = SessionLocal()
    try:
        # We limit the dump to 100 to ensure the browser doesn't hang/crash
        municipalities = db.query(Municipality).limit(100).all()
        officials = db.query(MunicipalityOfficial).all()
        
        # Map officials to their respective municipalities
        official_map = defaultdict(list)
        for o in officials:
            official_map[o.municipality_id].append(o)
        
        full_data = []
        for mun in municipalities:
            related_officials = official_map.get(mun.id, [])
            full_data.append({
                "municipality_info": {
                    "id": mun.id,
                    "name": mun.municipality_name,
                    "district": mun.district,
                    "province": mun.province,
                    "website": mun.website,
                    "phone": getattr(mun, 'phone', None)
                },
                "officials": [{
                    "mayor": o.mayor_name, 
                    "mayor_email": o.mayor_email,
                    "mayor_phone": o.mayor_phone, 
                    "deputy": o.deputy_mayor_name,
                    "deputy_phone": o.deputy_mayor_phone,
                    "deputy_email": o.deputy_mayor_email
                } for o in related_officials]
            })
        return full_data
    except Exception as e:
        print(f"Error in full database dump: {e}")
        return []
    finally:
        db.close()

    
def get_export_data():

    db = SessionLocal()

    try:

        municipalities = db.query(
            Municipality
        ).all()

        export_rows = []

        for mun in municipalities:

            officials = db.query(
                MunicipalityOfficial
            ).filter(
                MunicipalityOfficial.municipality_id == mun.id
            ).all()

            if officials:

                for o in officials:

                    export_rows.append({
                        "Province": mun.province,
                        "District": mun.district,
                        "Municipality": mun.municipality_name,
                        "Type": mun.municipality_type,
                        "Website": mun.website,
                        "Email": mun.email,
                        "Phone": mun.phone,

                        "Mayor": o.mayor_name,
                        "Mayor Email": o.mayor_email,
                        "Mayor Phone": o.mayor_phone,

                        "Deputy Mayor": o.deputy_mayor_name,
                        "Deputy Email": o.deputy_mayor_email,
                        "Deputy Phone": o.deputy_mayor_phone,
                    })

            else:

                export_rows.append({
                    "Province": mun.province,
                    "District": mun.district,
                    "Municipality": mun.municipality_name,
                    "Type": mun.municipality_type,
                    "Website": mun.website,
                    "Email": mun.email,
                    "Phone": mun.phone,
                })

        return export_rows

    finally:
        db.close()    

def export_municipalities_to_csv(limit=20):

    db = SessionLocal()

    try:
        municipalities = db.query(Municipality).limit(limit).all()

        rows = []

        for mun in municipalities:

            official = (
                db.query(MunicipalityOfficial)
                .filter(
                    MunicipalityOfficial.municipality_id == mun.id
                )
                .first()
            )

            rows.append({
                "Province": mun.province,
                "District": mun.district,
                "Municipality": mun.municipality_name,
                "Type": mun.municipality_type,
                "Website": mun.website,
                "Email": mun.email,
                "Phone": mun.phone,

                "Mayor": official.mayor_name if official else "",
                "Mayor Email": official.mayor_email if official else "",
                "Mayor Phone": official.mayor_phone if official else "",

                "Deputy Mayor": official.deputy_mayor_name if official else "",
                "Deputy Email": official.deputy_mayor_email if official else "",
                "Deputy Phone": official.deputy_mayor_phone if official else "",
            })

        df = pd.DataFrame(rows)

        file_path = f"exports/municipality_export_{limit}.csv"

        df.to_csv(
            file_path,
            index=False,
            encoding="utf-8-sig"
        )

        return file_path

    finally:
        db.close()    

def get_multiple_municipalities(limit=20):

    db = SessionLocal()

    try:

        if limit == -1:
            municipalities = db.query(Municipality).all()
        else:
            municipalities = (
                db.query(Municipality)
                .limit(limit)
                .all()
            )

        results = []

        for mun in municipalities:

            official = (
                db.query(MunicipalityOfficial)
                .filter(
                    MunicipalityOfficial.municipality_id == mun.id
                )
                .first()
            )

            results.append({
                "province": mun.province,
                "district": mun.district,
                "municipality": mun.municipality_name,
                "type": mun.municipality_type,
                "website": mun.website,
                "email": mun.email,
                "phone": mun.phone,

                "mayor": official.mayor_name if official else "",
                "mayor_phone": official.mayor_phone if official else "",

                "deputy_mayor": (
                    official.deputy_mayor_name
                    if official else ""
                ),
                "deputy_phone": (
                    official.deputy_mayor_phone
                    if official else ""
                )
            })

        return results

    finally:
        db.close()