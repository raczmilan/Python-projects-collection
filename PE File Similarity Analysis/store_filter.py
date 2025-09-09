import pickle
import sqlite3
import hashlib
import extract as ex
from pathlib import Path


def create_homeworks_table(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Homeworks
                      (Hash TEXT, Assign TEXT, Student TEXT, Ngrams BLOB)''')
    connection.commit()


def insert_homework(connection, hash_value, assign, student_id, ngrams):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO Homeworks (Hash, Assign, Student, Ngrams)
                      VALUES (?, ?, ?, ?)''', (hash_value, assign, student_id, ngrams))
    connection.commit()


def select_all_homeworks(db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    try:
        cursor.execute('''SELECT * FROM Homeworks''')
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return

    rows = cursor.fetchall()
    for row in rows:
        ngrams_set = pickle.loads(row[3])
        print([row[0], row[1], row[2], ngrams_set])

    connection.close()


def hash_file(path):
    with open(path, 'rb') as f:
        hasher = hashlib.sha1()
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()


def create_features_raw(path):
    connection = sqlite3.connect('features_raw.db')
    create_homeworks_table(connection)
    try:
        directory = Path(path)
        for file_path in directory.iterdir():
            if file_path.is_file():
                name_without_extension, extension = file_path.name.split('.')
                if extension == "exe":
                    assign, student_id = name_without_extension.split('_')
                    file_hash = hash_file(file_path)
                    ngrams_blob = pickle.dumps(ex.get_ngrams(file_path))
                    insert_homework(connection, file_hash, assign, student_id, ngrams_blob)

    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return

    connection.close()


def get_elements_from_db():
    connection = sqlite3.connect('features_raw.db')
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT * FROM Homeworks''')
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return None

    entry_list = []
    for row in rows:
        ngrams_set = pickle.loads(row[3])
        entry_list.append([row[0], row[1], row[2], ngrams_set])

    connection.close()
    return entry_list


def create_features():
    entry_list = get_elements_from_db()
    if entry_list is None:
        print("Error")
        return

    ngram_counts = {}
    for entry in entry_list:
        for ngram in entry[3]:
            ngram_counts[ngram] = ngram_counts.get(ngram, 0) + 1

    elements_to_remove = []

    for ngram, count in ngram_counts.items():
        if count >= 30:
            elements_to_remove.append(ngram)

    elements_to_remove = set(elements_to_remove)

    connection = sqlite3.connect('features.db')
    create_homeworks_table(connection)

    for entry in entry_list:
        entry[3] -= elements_to_remove
        ngrams_blob = pickle.dumps(entry[3])
        insert_homework(connection, entry[0], entry[1], entry[2], ngrams_blob)

    connection.close()


def sim1(db, h1, h2):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT Ngrams FROM Homeworks WHERE Hash = ?''', (h1, ))
        row1 = cursor.fetchall()
        cursor.execute('''SELECT Ngrams FROM Homeworks WHERE Hash = ?''', (h2, ))
        row2 = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return None

    if len(row1) > 0 and len(row2) > 0:
        similarity = ex.jaccard_similarity(pickle.loads(row1[0][0]), pickle.loads(row2[0][0]))
        connection.close()
        return similarity
    else:
        connection.close()
        return 0


def sim2(db, assign, s1, s2):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT Ngrams FROM Homeworks WHERE Assign = ? AND Student = ?''', (assign, s1))
        row1 = cursor.fetchall()
        cursor.execute('''SELECT Ngrams FROM Homeworks WHERE Assign = ? AND Student = ?''', (assign, s2))
        row2 = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return None

    if len(row1) > 0 and len(row2) > 0:
        similarity = ex.jaccard_similarity(pickle.loads(row1[0][0]), pickle.loads(row2[0][0]))
        connection.close()
        return similarity
    else:
        connection.close()
        return 0


def get_students(db, assign):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT Student FROM Homeworks WHERE Assign = ?''', (assign,))
        row = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return None
    connection.close()
    if len(row) > 0:
        return row
    else:
        return None


def top500(db):
    similarities = {}
    for a in range(11):
        if a < 9:
            assign = "a0" + str(a+1)
        else:
            assign = "a" + str(a+1)

        student_list = get_students(db, assign)
        if student_list is None:
            continue
        for i in range(len(student_list)):
            for j in range(i + 1, len(student_list)):
                similarity = sim2(db, assign, student_list[i][0], student_list[j][0])
                entry = assign + "_" + student_list[i][0] + " - " + assign + "_" + student_list[j][0]
                similarities[entry] = similarity

    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    name_without_extension, extension = db.split('.')

    path = './' + name_without_extension + '.txt'

    with open(path, 'w', encoding='utf-8') as f:
        for i in range(min(500, len(sorted_similarities))):
            f.write(str(i + 1) + ". " + str(sorted_similarities[i][0]) + ": " + str(sorted_similarities[i][1]) + "\n")


if __name__ == '__main__':
    while True:
        command = input("Enter \"raw\"/\"features\"/\"sim1\"/\"sim2\"/\"top\"/\"print\"/\"exit\": ")
        if command == "raw":
            directory_path = input("Enter path: ")
            create_features_raw(directory_path)
        elif command == "features":
            create_features()
        elif command == "print":
            database = input("Enter database name: ")
            select_all_homeworks(database)
        elif command == "sim1":
            database = input("Enter database name: ")
            hash1 = input("Enter hash1: ")
            hash2 = input("Enter hash2: ")
            sim = sim1(database, hash1, hash2)
            print("Jaccard similarity: " + str(sim))
        elif command == "sim2":
            database = input("Enter database name: ")
            assignment = input("Enter assignment: ")
            student1 = input("Enter student1: ")
            student2 = input("Enter student2: ")
            sim = sim2(database, assignment, student1, student2)
            print("Jaccard similarity: " + str(sim))
        elif command == "top":
            database = input("Enter database name: ")
            top500(database)
        elif command == "exit":
            break

        print("\n")
