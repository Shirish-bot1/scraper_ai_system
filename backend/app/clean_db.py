import re

from app.database.db import SessionLocal
from app.models.municipality import Municipality
from app.models.municipality_official import MunicipalityOfficial


def has_letters(phone):
    """Returns True if phone contains any English letters."""
    if not phone:
        return False
    return bool(re.search(r"[A-Za-z]", phone))


def clean_database():
    db = SessionLocal()

    # Delete municipalities with empty names
    deleted_municipalities = (
        db.query(Municipality)
        .filter(
            (Municipality.municipality_name == None)
            | (Municipality.municipality_name == "")
        )
        .delete(synchronize_session=False)
    )

    # Delete municipality officials with invalid phone numbers
    officials = db.query(MunicipalityOfficial).all()

    deleted_officials = 0

    for official in officials:
        if (
            has_letters(official.mayor_phone)
            or has_letters(official.deputy_mayor_phone)
        ):
            print(
                f"Deleting {official.municipality_name} "
                f"(Mayor: {official.mayor_phone}, "
                f"Deputy: {official.deputy_mayor_phone})"
            )

            db.delete(official)
            deleted_officials += 1

    db.commit()
    db.close()

    print(f"Deleted {deleted_municipalities} empty municipalities.")
    print(f"Deleted {deleted_officials} officials with invalid phone numbers.")


if __name__ == "__main__":
    clean_database()