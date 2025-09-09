Image-Based Clustering



A simple clustering algorithm was implemented to group points in binary images based on spatial connectivity. Each image is scanned, and points (black pixels) are assigned to clusters through a connected component labeling process: if two points are within a given neighborhood radius r, they are considered part of the same cluster.



The algorithm assigns a unique label to each cluster and generates a visualization where points are recolored according to their cluster membership. Additionally, the program counts the number of neighbor checks performed during clustering.

