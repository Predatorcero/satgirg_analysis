import math
import string
import os

import graphviz as gv
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def read_graph(filename: string):
    try:
        first_line = True
        second_line = False
        edge_list = []
        with open(filename) as f:
            for line in f:
                if first_line:
                    first_line = False
                    second_line = True
                    continue
                elif second_line:
                    second_line = False
                    continue
                line = line.replace("\n", "")
                edge = line.split(" ")
                edge_list.append((int(edge[0]), int(edge[1])))

        return nx.Graph(edge_list)

    except IOError as e:
        print(f"Error when reading the graph: {e}")
        return None


def get_largest_connected_component(g: nx.Graph):
    return g.subgraph(max(nx.connected_components(g), key=len))


def get_chunks_of_graph(directory: string):
    filenames = os.listdir(directory)
    graph_dict = {}
    counter = 0
    for filename in filenames:
        if filename.endswith(".txt"):
            ple_index = filename.index("_ple") + len("_ple")
            t_index = filename.index("_t") + len("_t")
            key = f"ple{filename[ple_index]}_t{filename[t_index]}"
            if graph_dict.get(key) is None:
                graph_dict[key] = []
            graph_dict[key].append(get_largest_connected_component(read_graph(f"{directory}/{filename}")))
            counter += 1

            # logging
            if (counter % 5) == 0:
                print(filename)

    return graph_dict


def calculate_heterogeneity(g: nx.Graph):
    degrees = [g.degree(n) for n in g.nodes]
    number_of_vertices = len(g.nodes)
    avg_degree = sum(degrees) / number_of_vertices
    sum_squared_deviation = 0
    for d in degrees:
        sum_squared_deviation += (d - avg_degree) ** 2

    variance = sum_squared_deviation / number_of_vertices
    # standard deviation relative to the mean
    coefficient_of_variation = math.sqrt(variance) / avg_degree
    heterogeneity = math.log10(coefficient_of_variation)
    return heterogeneity


def calculate_clustering_coefficient(g: nx.Graph):
    return nx.average_clustering(g)


def generate_heterogeneity_locality_csv(graph_dict: dict):
    heterogeneity_list = []
    locality_list = []
    measurement_entries = []

    for param_key in graph_dict:
        sum_heterogeneity = 0
        sum_locality = 0
        for graph in graph_dict[param_key]:
            sum_heterogeneity += calculate_heterogeneity(graph)
            sum_locality += calculate_clustering_coefficient(graph)

        heterogeneity_measurement = sum_heterogeneity / len(graph_dict[param_key])
        locality_measurement = sum_locality / len(graph_dict[param_key])
        # heterogeneity_list.append(heterogeneity_measurement)
        # locality_list.append(locality_measurement)
        measurement_entries.append({"param_config": param_key, "heterogeneity": heterogeneity_measurement,
                                    "locality": locality_measurement})

        # logging
        print(f"added point for parameter configuration {param_key}")

    heterogeneity_locality_df = pd.DataFrame(measurement_entries)
    heterogeneity_locality_df.to_csv("girg_heterogeneity_locality_experiment.csv")
    plt.scatter(heterogeneity_list, locality_list)
    plt.show()


def plot_heterogeneity_locality(csv):
    df = pd.read_csv(csv)
    heterogeneity_list = df["heterogeneity"].tolist()
    locality_list = df["locality"].tolist()
    plt.scatter(heterogeneity_list, locality_list)
    plt.show()


def plot_degree_distribution(g: nx.Graph):
    degrees = [g.degree(n) for n in g.nodes]
    plt.hist(degrees, list(range(1, 15)))
    plt.show()


def plot_number_of_edges(directory, xlabel="", ylabel=""):
    num_edges = []
    filenames = os.listdir(directory)
    for filename in filenames:
        if filename.endswith(".txt"):
            g = read_graph(directory + "/" + filename)
            num_edges.append(len(g.edges))

    plt.scatter(list(range(0, int(len(filenames) / 2))), num_edges)
    # plt.plot([100_000, 250_000, 300_000, 400_000, 500_000, 600_000, 700_000, 800_000, 900_000, 1_000_000], num_edges)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


if __name__ == '__main__':
    # plot_heterogeneity_locality("satgirg_heterogeneity_locality_experiment.csv")
    chunked_graphs = get_chunks_of_graph("graph_chunks/girgs")
    generate_heterogeneity_locality_csv(chunked_graphs)
