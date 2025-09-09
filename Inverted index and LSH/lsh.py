import sqlite3
import invertedIndex as inv
import hashlib
import ast

m = 1000
b = 30
r = 5
A = []
B = []


def custom_hash(input_string):
    input_bytes = input_string.encode('utf-8')
    hash_object = hashlib.sha256(input_bytes)
    hash_hex = hash_object.hexdigest()
    return int(hash_hex, 16)


def minhash(s, band, row):
    a = A[band * r + row]
    b = B[band * r + row]
    perm = [(a*abs(custom_hash(x))+b) % m for x in s]
    if len(perm) > 0:
        return min(perm)
    else:
        return 0


def compute_bands(content):
    bands = []
    for band in range(b):
        h = []
        for row in range(r):
            h.append(minhash(content, band, row))
        bands.append(h)
    return bands


def create_lsh():
    connection = sqlite3.connect('lsh.db')
    cursor = connection.cursor()

    hash_columns = ",\n".join(f"Hash{i} TEXT" for i in range(1, b + 1))

    create_table_query = f'''CREATE TABLE IF NOT EXISTS LSH (
                                Assign TEXT,
                                Student TEXT,
                                {hash_columns}
                             )'''

    cursor.execute(create_table_query)
    connection.commit()


def insert_lsh(connection, lsh_row):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO LSH VALUES ({})'''.format(','.join(['?'] * len(lsh_row))), lsh_row)
    connection.commit()


def select_all_lsh():
    connection = sqlite3.connect('lsh.db')
    cursor = connection.cursor()

    try:
        cursor.execute('''SELECT * FROM LSH''')
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return

    rows = cursor.fetchall()
    for row in rows:
        print(row)

    connection.close()


def lsh():
    create_lsh()
    entry_list = inv.get_features()
    connection = sqlite3.connect('lsh.db')

    for entry in entry_list:
        assign = entry[1]
        student = entry[2]
        sorted_set = sorted(entry[3])
        hashes = compute_bands(sorted_set)
        lsh_row = [assign, student] + [str(band) for band in hashes]
        insert_lsh(connection, lsh_row)

    connection.commit()
    connection.close()


def get_lsh():
    connection = sqlite3.connect('lsh.db')
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT * FROM LSH''')
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        return None

    lsh_list = []
    for row in rows:
        lsh_list.append([row[0], row[1], row[2:]])

    connection.close()
    return lsh_list


def create_groups():
    band_groups = [{} for i in range(b*r)]
    lsh_list = get_lsh()
    for assign, student, bands in lsh_list:
        for band, H in enumerate(bands):
            if H in band_groups[band]:
                band_groups[band][H].add(assign + "_" + student)
            else:
                band_groups[band][H] = {assign + "_" + student}
    return band_groups


def search_lsh(assign, student, threshold, p):
    band_groups = create_groups()
    content = inv.get_content(assign, student)
    sorted_content = sorted(content)
    hashes = compute_bands(sorted_content)
    bands = [str(band) for band in hashes]
    elements_to_remove = {assign + "_" + student}
    candidates = set()

    for band, H in enumerate(bands):
        if H in band_groups[band]:
            for element in band_groups[band][H]:
                assign2, student2 = element.split('_')
                if assign != assign2:
                    elements_to_remove.add(element)
            candidates |= (band_groups[band][H])

    candidates -= elements_to_remove

    for file in candidates:
        assign, student = file.split('_')
        doc_content = inv.get_content(assign, student)

        similarity = inv.jaccard(content, doc_content)

        if similarity >= threshold:
            if p:
                print(file)
            else:
                inv.similar_files += 1


def test():
    inv.student_count = 0
    inv.similar_files = 0
    inv.call_count = 0

    for a in range(11):
        if a < 9:
            assign = "a0" + str(a + 1)
        else:
            assign = "a" + str(a + 1)

        student_list = inv.get_students(assign)
        if student_list is None:
            continue
        for i in range(len(student_list)):
            inv.student_count += 1
            search_lsh(assign, student_list[i][0], 0.7, False)

    print("Average number of distance function calls: " + str(inv.call_count/inv.student_count))
    print("Average number of similar files: " + str(inv.similar_files/inv.student_count))


def main():
    with open('A_B.txt', 'r') as file:
        lines = file.readlines()

    global A, B
    A = ast.literal_eval(lines[0])
    B = ast.literal_eval(lines[1])

    while True:
        command = input("Enter \"lsh\"/\"search\"/\"print\"/\"test\"/\"exit\": ")
        if command == "lsh":
            lsh()
        elif command == "g":
            create_groups()
        elif command == "search":
            name = input("Enter file name: ")  # a good example is a03_s0105 with a threshold of 0.7
            threshold = input("Enter threshold: ")
            inv.call_count = 0
            try:
                assign, student = name.split('_')
                search_lsh(assign, student, float(threshold), True)
            except Exception as e:
                print(f"Error: {e}")
                print("\n")
                continue
            print("Call count: " + str(inv.call_count))
        elif command == "print":
            select_all_lsh()
        elif command == "test":
            test()
        elif command == "exit":
            break

        print("\n")


if __name__ == "__main__":
    main()
