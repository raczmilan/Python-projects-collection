Advanced Search Techniques



Building on the features.db database (see "PE File Similarity Analysis"), additional search methods were implemented to efficiently detect similar files. An inverted index (inverted.db) was created to map n-grams to the files where they appear, enabling similarity queries via the search\_inv() function. To improve scalability, locality-sensitive hashing (LSH) was also applied, with results stored in lsh.db and queried through search\_lsh(). The two approaches were compared, both in terms of retrieved results and the average number of distance computations required.

