import random
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Graph:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.adj_list = {i: [] for i in range(num_nodes)}

    def add_edge(self, src, dest):
        if src < 0 or src >= self.num_nodes or dest < 0 or dest >= self.num_nodes:
            raise ValueError("Invalid node index")
        self.adj_list[src].append(dest)

    def adjacency_matrix(self):
        matrix = [[0] * self.num_nodes for _ in range(self.num_nodes)]
        for src, neighbors in self.adj_list.items():
            for dest in neighbors:
                matrix[src][dest] = 1
        return matrix


def distance(vector1, vector2):
    distance = np.linalg.norm(vector1 - vector2)
    return distance


def show_chart(vectors):
    root = Tk()
    root.title("Multiple Charts with Notebook")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    for i, v in enumerate(vectors):
        tab_frame = Frame(notebook)
        tab_frame.pack(fill='both', expand=True)

        fig, ax = plt.subplots(figsize=(6, 4))
        indices = np.arange(len(v))
        ax.bar(indices, v)
        ax.set_xlabel('Index')
        ax.set_ylabel('Value')
        ax.set_title(f'Vector {i + 1}')

        canvas = FigureCanvasTkAgg(fig, master=tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

        notebook.add(tab_frame, text=f"Vector {i + 1}")
    root.mainloop()


if __name__ == "__main__":
    graph = Graph(10)
    num_edges = 25
    edges_added = set()

    while len(edges_added) < num_edges:
        n1 = random.randint(0, 9)
        n2 = random.randint(0, 9)
        if n1 != n2 and (n1, n2) not in edges_added:
            graph.add_edge(n1, n2)
            edges_added.add((n1, n2))

    adj_matrix = graph.adjacency_matrix()

    for row in adj_matrix:
        print(row)

    value = 1/10
    vector = np.full(graph.num_nodes, value)

    vector_list = []

    while True:
        vector_list.append(vector)
        result = np.dot(adj_matrix, vector)

        total = np.sum(result)
        result /= total

        if distance(result, vector) < 0.005:
            break

        vector = result

    show_chart(vector_list)
