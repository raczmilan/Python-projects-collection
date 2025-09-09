import re
import dummyMapReduce as mr

rxWord = re.compile(r"[a-zA-Z]{3,}")

DOCUMENTS = [
    ("doc1", """MapReduce is a programming model and an associated implementation for processing and generating large
                    data sets with a parallel, distributed algorithm on a cluster."""),
    ("doc2", """Conceptually similar approaches have been very well known since 1995 with the Message Passing
                    Interface standard having reduce and scatter operations."""),
    ("doc3", """A MapReduce program is composed of a Map() procedure (method) that performs filtering and sorting
                (such as sorting students by first name into queues, one queue for each name) and a Reduce() method
                that performs a summary operation (such as counting the number of students in each queue, yielding
                name frequencies)."""),
    ("doc4", """The "MapReduce System" (also called "infrastructure" or "framework") orchestrates the processing by
                marshalling the distributed servers, running the various tasks in parallel, managing all
                communications and data transfers between the various parts of the system, and providing for
                redundancy and fault tolerance."""),
    ("doc5", """The model is inspired by the map and reduce functions commonly used in functional programming,
                although their purpose in the MapReduce framework is not the same as in their original forms."""),
    ("doc6", """The key contributions of the MapReduce framework are not the actual map and reduce functions, but
                the scalability and fault-tolerance achieved for a variety of applications by optimizing the
                execution engine once"""),
    ("doc8", """As such, a single-threaded implementation of MapReduce will usually not be faster than a traditional
                (non-MapReduce) implementation, any gains are usually only seen with multi-threaded implementations"""),
    ("doc9", """The use of this model is beneficial only when the optimized distributed shuffle operation
                (which reduces network communication cost) and fault tolerance features of the MapReduce framework
                come into play."""),
    ("doc10", """Optimizing the communication cost is essential to a good MapReduce algorithm.""")
]


class WordCounter(mr.MapReduce):
    def map(self, _fileName, content):
        words = rxWord.findall(content)
        word_list = []
        for word in words:
            count = 0
            if word not in word_list:
                for word2 in words:
                    if word2 == word:
                        count += 1
                word_list.append(word)
                self.emit(word.lower(), count)

    def reduce(self, word, counts):
        wordCount = 0
        for count in counts:
            wordCount += count
        print(word, wordCount)


def main():
    wc = WordCounter()
    wc.run(DOCUMENTS)


if __name__ == "__main__":
    main()
