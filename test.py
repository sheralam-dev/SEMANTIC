from app.storage import db
# from app.storage import repository as repo
# from app.search.embedding_model import load_model

def main():
    print("Hello from semantic!")
    # load_model()
    db.init_db(drop_tables=False)
    rows = db.get_connection().execute("select name from files").fetchall()
    for row in rows:
        print(row[0], end=' | ')
    # print(len(rows))
    rows = db.get_connection().execute("select name from files_vector").fetchall()
    print()
    for row in rows:
        print(row[0], end=' | ')
    # print(len(rows))
    print()
    print("===" * 20)

    # repo.s

if __name__ == "__main__":
    # main()
    db.init_db(drop_tables=True)
    count = db.get_connection().execute("select count(name) from files_vector").fetchone()
    print(f'rows {count = }')