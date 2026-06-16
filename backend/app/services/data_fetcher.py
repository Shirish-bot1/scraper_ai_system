from collections import defaultdict
from app.database.db import SessionLocal
from app.models.municipality import Municipality
from app.models.municipality_official import MunicipalityOfficial

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