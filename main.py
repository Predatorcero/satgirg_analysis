import math
import string
import os

import graphviz as gv
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bson import ObjectId
from database_setup import insert_experiment_to_db, insert_datapoint, experiments_for_platform, data_from_experiment, delete_experiment_from_db


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


def calculate_average_degree(g: nx.Graph):
    degrees = [g.degree(n) for n in g.nodes]
    number_of_vertices = len(g.nodes)
    return sum(degrees) / number_of_vertices


def calculate_diameter(g: nx.Graph):
    return nx.diameter(g)


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


def calculate_properties(graph_dict: dict, experiment_id: ObjectId):
    measurement_entries = []

    for param_key in graph_dict:
        sum_number_of_nodes = 0
        sum_number_of_edges = 0
        sum_average_degree = 0
        # sum_diameter = 0
        sum_heterogeneity = 0
        sum_clustering = 0
        for graph in graph_dict[param_key]:
            sum_number_of_nodes += graph.number_of_nodes()
            sum_number_of_edges += graph.number_of_edges()
            sum_average_degree += calculate_average_degree(graph)
            # sum_diameter += calculate_diameter(graph)
            sum_heterogeneity += calculate_heterogeneity(graph)
            sum_clustering += calculate_clustering_coefficient(graph)

        number_of_nodes_measurement = sum_number_of_nodes / len(graph_dict[param_key])
        number_of_edges_measurement = sum_number_of_edges / len(graph_dict[param_key])
        average_degree_measurement = sum_average_degree / len(graph_dict[param_key])
        # diameter_measurement = sum_diameter / len(graph_dict[param_key])
        heterogeneity_measurement = sum_heterogeneity / len(graph_dict[param_key])
        clustering_measurement = sum_clustering / len(graph_dict[param_key])
        insert_datapoint(experiment_id,
                         {"param_config": param_key,
                          "number_of_nodes": round(number_of_nodes_measurement),
                          "number_of_edges": round(number_of_edges_measurement),
                          "average_degree": average_degree_measurement,
                          # "diameter": diameter_measurement,
                          "heterogeneity": heterogeneity_measurement,
                          "average_clustering": clustering_measurement},
                         "thesis_nicola")

        # logging
        print(f"added point for parameter configuration {param_key}")


def plot_heterogeneity_locality(csv):
    df = pd.read_csv(csv)
    heterogeneity_list = df["heterogeneity"].tolist()
    locality_list = df["average_clustering"].tolist()
    plt.scatter(heterogeneity_list, locality_list)
    plt.show()


def plot_heterogeneity_locality_difference(girg_csv, satgirg_csv):
    girg_df = pd.read_csv(girg_csv)
    satgirg_df = pd.read_csv(satgirg_csv)

    fig, ax = plt.subplots()
    girg_edges = girg_df["number_of_edges"].tolist()
    satgirg_edges = satgirg_df["number_of_edges"].tolist()
    zs = np.concatenate([girg_edges, satgirg_edges], axis=0)
    min_, max_ = zs.min(), zs.max()

    girg_heterogeneity_list = girg_df["heterogeneity"].tolist()
    girg_locality_list = girg_df["average_clustering"].tolist()
    satgirg_heterogeneity_list = satgirg_df["heterogeneity"].tolist()
    satgirg_locality_list = satgirg_df["average_clustering"].tolist()
    plt.scatter(girg_heterogeneity_list, girg_locality_list, c=girg_edges, label="girgs", cmap='viridis_r', marker='s')
    plt.clim(min_, max_)
    plt.scatter(satgirg_heterogeneity_list, satgirg_locality_list, c=satgirg_edges, label="satgirgs", cmap='viridis_r', marker='o')
    plt.clim(min_, max_)
    plt.colorbar().set_label('number of edges', rotation=270, labelpad=15)

    plt.xlabel("heterogeneity")
    plt.ylabel("average clustering")
    plt.legend()
    plt.show()


def plot_degree_distribution(g: nx.Graph):
    degrees = [g.degree(n) for n in g.nodes]
    plt.hist(degrees, list(range(1, 15)))
    plt.show()


def plot_number_of_vertices_edges_relation(graphs: string):
    df = pd.read_csv(graphs)
    param_configs = df["param_config"].tolist()
    number_of_vertices = df["number_of_nodes"].tolist()
    number_of_edges = df["number_of_edges"].tolist()
    plt.scatter(number_of_vertices, number_of_edges)
    plt.xlabel("number of vertices")
    plt.ylabel("number of edges")
    plt.show()



if __name__ == '__main__':
    # chunked_graphs = get_chunks_of_graph("power_law_temperature_graphs/second_girgs")
    # generate_csv("girg_low_temperature_properties.csv", chunked_graphs)
    plot_number_of_vertices_edges_relation("measurements/satgirg_properties.csv")
    # plot_heterogeneity_locality_difference("measurements/girg_properties.csv", "measurements/satgirg_properties.csv")
    # delete_experiment_from_db("test-girg-properties", "thesis_nicola")
    experiments_df = experiments_for_platform("thesis_nicola")
    # data = data_from_experiment(ObjectId("6462b15e40fecf008c787eb4"), "thesis_nicola")
    data = data_from_experiment(ObjectId("646397c7d6b97248fd04bae0"), "thesis_nicola")
    experiment_id = insert_experiment_to_db("test-girg-properties", "thesis_nicola")
    chunked_graphs = get_chunks_of_graph("power_law_temperature_graphs/girgs")
    calculate_properties(chunked_graphs, experiment_id)
    # plot_heterogeneity_locality("satgirg_heterogeneity_locality_experiment.csv")
