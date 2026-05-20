from pathlib import Path

from app.storage import db
from app.storage.models import File


if __name__ == "__main__":
    db.init_db(drop_tables=True)
    # count = db.get_connection().execute("select count(*) from files_vector").fetchone()
    # print(f'rows {count = }')


    # f = File(Path("D:\my-workspace\semantic\config.json"))
    # print(f.date_modified)

    print(f'{342353:,}')