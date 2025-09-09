import os
from PIL import Image
import numpy as np


width = 0
height = 0
n = 0
r = 1


def image_to_data(image_path):
    global width, height
    img = Image.open(image_path)
    width, height = img.size
    pixel_array = [[0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            if pixel == 0 or pixel == (0, 0, 0, 255):
                pixel_array[y][x] = 1
            else:
                pixel_array[y][x] = 0
    return pixel_array


def get_neighbors(row, col):
    global n, r
    neighbors = []
    for i in range(-r, r + 1):
        for j in range(-r, r + 1):
            if i == 0 and j == 0:
                continue
            if 0 <= row + i < height and 0 <= col + j < width:
                n += 1
                neighbors.append((row + i, col + j))
    return neighbors


label = 1


def connected_component_labeling(image):
    global height, width, label, n
    labels = [[0 for _ in range(width)] for _ in range(height)]
    cluster_list = []

    for i in range(height):
        for j in range(width):
            if image[i][j] == 1 and labels[i][j] == 0:
                k = 1
                seed = (i, j)
                cluster_list.append((i, j))
                labels[i][j] = label
                while True:
                    current_row, current_col = seed
                    neighbors = get_neighbors(current_row, current_col)
                    for neighbor in neighbors:
                        x, y = neighbor
                        if image[x][y] == 1 and labels[x][y] == 0:
                            cluster_list.append((x, y))
                            labels[x][y] = label
                    if len(cluster_list) == k:
                        cluster_list = []
                        break
                    else:
                        seed = cluster_list[k]
                        k += 1

                label += 1

    return labels


def create_cluster_image(labels):
    global height, width

    color_map = {0: (255, 255, 255)}
    label_image = np.zeros((height, width, 3), dtype=np.uint8)
    used_colors = set()

    for row in range(height):
        for col in range(width):
            pixel = labels[row][col]
            if pixel not in color_map:
                new_color = tuple(np.random.randint(0, 256, 3))
                while new_color in used_colors:
                    new_color = tuple(np.random.randint(0, 256, 3))
                used_colors.add(new_color)
                color_map[pixel] = new_color
            label_image[row][col] = color_map[pixel]

    label_image = Image.fromarray(label_image, 'RGB')
    label_image.show()


if __name__ == "__main__":
    r = input("Enter r: ")
    r = int(r)
    dir_path = "./dataset/"
    for filename in os.listdir(dir_path):
        path = os.path.join(dir_path, filename)
        if os.path.isfile(path):
            pixels = image_to_data(path)
            label_matrix = connected_component_labeling(pixels)
            create_cluster_image(label_matrix)

    print("Neighbor cells clustering call count: " + str(n))
