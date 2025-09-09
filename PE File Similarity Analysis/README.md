PE File Similarity Analysis



This project analyzes Windows Portable Executable (PE) files by extracting general metadata (e.g., platform type, number of sections, number of executable sections, entry points) and disassembling executable sections. The disassembled instructions are normalized (e.g., removing NOP, INT 3, grouping equivalent operations such as ADD/SUB/INC) and represented as 5-grams. Program similarity is then measured using the Jaccard index.



The extracted information (assignment/student identifiers, file hashes, and n-grams) is stored in a database (features.db). To reduce noise, n-grams that occur in 30 or more files are filtered out, eliminating common compiler-generated or library code. The database can then be queried to compare two files directly using Jaccard similarity or to retrieve the top 500 most similar file pairs for large-scale analysis.

