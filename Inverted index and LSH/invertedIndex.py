import pickle
import sqlite3
import dummyMapReduce as mr


def create_inverted_table(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Homeworks
                      (Ngram TEXT, Files BLOB)''')
    connection.commit()


def insert_homework(connection, ngram, files):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO Homeworks (Ngram, Files)
                      VALUES (?, ?)''', (ngram, files))
    connection.commit()


def select_all_homeworks():
    connection = sqlite3.connect('inverted.db')
    cursor = connection.cursor()

    try:
        cursor.execute('''SELECT * FROM Homeworks''')
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return

    rows = cursor.fetchall()
    for row in rows:
        file_set = pickle.loads(row[1])
        print([row[0], file_set])

    connection.close()


def get_content(assign, student):
    connection = sqlite3.connect('features.db')
    cursor = connection.cursor()

    try:
        cursor.execute('''SELECT Ngrams FROM Homeworks WHERE Assign = ? AND Student = ?''', (assign, student))
        row = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return None

    if len(row) > 0:
        connection.close()
        return pickle.loads(row[0][0])
    else:
        connection.close()
        return 0


def get_features():
    connection = sqlite3.connect('features.db')
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


def get_inverted():
    connection = sqlite3.connect('inverted.db')
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
        file_list = pickle.loads(row[1])
        entry_list.append([row[0], file_list])

    connection.close()

    dictionary = {inner_list[0]: inner_list[1] for inner_list in entry_list}

    return dictionary


call_count = 0
similar_files = 0
student_count = 0


def jaccard(content, doc_content):
    global call_count
    call_count += 1
    intersection = len(content.intersection(doc_content))
    union = len(content.union(doc_content))
    return intersection / union if union else 0


def search_inv(assign, student, threshold, p):
    global similar_files

    inverted_index = get_inverted()
    if inverted_index is None:
        print("Error")
        return

    content = get_content(assign, student)

    candidates = set()
    for element in content:
        if element in inverted_index:
            for file in inverted_index[element]:
                if file[0] == assign and file[1] != student:
                    candidates.add(file)

    for assign, student in candidates:
        doc_content = get_content(assign, student)

        similarity = jaccard(content, doc_content)

        if similarity >= threshold:
            if p:
                print(assign + "_" + student)
            else:
                similar_files += 1


def get_students(assign):
    connection = sqlite3.connect('features.db')
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


def test():
    global student_count, similar_files, call_count
    student_count = 0
    similar_files = 0
    call_count = 0

    for a in range(11):
        if a < 9:
            assign = "a0" + str(a + 1)
        else:
            assign = "a" + str(a + 1)

        student_list = get_students(assign)
        if student_list is None:
            continue
        for i in range(len(student_list)):
            student_count += 1
            search_inv(assign, student_list[i][0], 0.7, False)

    print("Average number of distance function calls: " + str(call_count/student_count))
    print("Average number of similar files: " + str(similar_files/student_count))


class Inverter(mr.MapReduce):
    def run(self, collection):
        for file_hash, assign, student, ngrams in collection:
            self.map([assign, student], ngrams)

        connection = sqlite3.connect('inverted.db')
        create_inverted_table(connection)

        for key, values in self.data.items():
            self.reduce(connection, [key, values])

        connection.close()

    def map(self, file, ngrams):
        for ngram in ngrams:
            self.emit(ngram, file)

    def reduce(self, connection, data):
        file_blob = pickle.dumps(data[1])
        insert_homework(connection, data[0], file_blob)


def main():
    while True:
        command = input("Enter \"invert\"/\"search\"/\"print\"/\"test\"/\"exit\": ")
        if command == "invert":
            entry_list = get_features()
            if entry_list is None:
                print("Error")
                continue
            wc = Inverter()
            wc.run(entry_list)
        elif command == "search":
            name = input("Enter file name: ")  # a good example is a03_s0105 with a threshold of 0.7
            threshold = input("Enter threshold: ")
            global call_count
            call_count = 0
            try:
                assign, student = name.split('_')
                search_inv(assign, student, float(threshold), True)
            except Exception as e:
                print(f"Error: {e}")
                print("\n")
                continue
            print("Call count: " + str(call_count))
        elif command == "print":
            select_all_homeworks()
        elif command == "test":
            test()
        elif command == "exit":
            break

        print("\n")


if __name__ == "__main__":
    main()
