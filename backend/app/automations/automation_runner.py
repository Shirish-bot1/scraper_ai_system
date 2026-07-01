import subprocess


def run_scraper():
    print("Starting scraper...")

    subprocess.run(
        ["python", "app/scrapper/municipality_scraper.py"],
        check=True
    )

 

    print("Scraping completed")


def import_data():
    print("Importing CSV data...")

    subprocess.run(
        ["python", "-m", "app.import_municipalities"],
        check=True
    )

    subprocess.run(
        ["python", "-m", "app.import_municipalityofficial"],
        check=True
    )

    print("Import completed")

def clean_data():
    print("Cleaning the data")

    subprocess.run(
        ["python", "-m", "app.clean_db"],
        check=True

    )
def full_automation():
    run_scraper()
    import_data()
    clean_data()


if __name__ == "__main__":
    full_automation()