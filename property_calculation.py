import math
import os
import re
import random

from statistics import mean
import networkx as nx
from bson import ObjectId
from database_setup import insert_datapoint


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def read_graph(filename: str):
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


def get_vertices_edges_graph_chunks(directory: str):
    filenames = os.listdir(directory)
    graph_dict = {}
    counter = 0
    for filename in filenames:
        if filename.endswith(".txt"):
            number_list = re.findall('\d+', filename)
            key = f"{number_list[0]} {number_list[1]}"
            if graph_dict.get(key) is None:
                graph_dict[key] = []
            graph_dict[key].append(read_graph(f"{directory}/{filename}"))
            counter += 1

            # logging
            if (counter % 5) == 0:
                print(key)

    return graph_dict


def run_power_law_temperature_experiment(directory: str, experiment_id: ObjectId):
    filenames = os.listdir(directory)
    graph_dict = {}
    counter = 0
    for filename in filenames:
        if filename.endswith(".txt"):
            param_config = filename.split(sep='_')
            ple_value = param_config[2].split(sep="=")[1]
            t_value = param_config[3].split(sep="=")[1]
            if not is_number(ple_value):
                ple_value = "inf"
            if not is_number(t_value):
                t_value = "inf"
            key = f"{ple_value} {t_value}"
            if graph_dict.get(key) is None:
                graph_dict[key] = []
            graph_dict[key].append(get_largest_connected_component(read_graph(f"{directory}/{filename}")))
            counter += 1

            if (counter % 5) == 0:
                # logging
                print(key)
                calculate_properties(graph_dict, experiment_id)
                graph_dict = {}


def calculate_average_degree(g: nx.Graph):
    degrees = [g.degree(n) for n in g.nodes]
    number_of_vertices = len(g.nodes)
    return sum(degrees) / number_of_vertices


def calculate_diameter_approximation(g: nx.Graph):
    return nx.approximation.diameter(g)


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


def calculate_clustering_coefficient_approximation(g: nx.Graph):
    return nx.approximation.average_clustering(g, trials=50000, seed=1)


def calculate_clustering_coefficient(g: nx.Graph):
    return nx.average_clustering(g)


def calculate_average_shortest_path_approximation(n_samples=10_000, output_path='graph_info_output.txt'):
    graph_ = read_graph("power_law_temperature_graphs/low_temperature_satgirgs/n50000_m250000_ple0_t0_dimensions2_wseed1149_ncseed22406_cseed16546_eseed23817_satgirg1.txt")
    with open(output_path, encoding='utf-8', mode='w+') as f:
        for component in nx.connected_components(graph_):
            component_ = graph_.subgraph(component)
            nodes = component_.nodes()
            lengths = []
            counter = 0
            for _ in range(n_samples):
                n1, n2 = random.choices(list(nodes), k=2)
                length = nx.shortest_path_length(component_, source=n1, target=n2)
                lengths.append(length)
                print(counter, length)
                counter += 1
            f.write(f'Nodes num: {len(nodes)}, shortest path mean: {mean(lengths)} \n')


def calculate_basic_properties(graph_dict: dict, experiment_id: ObjectId):
    for param_key in graph_dict:
        param_config = param_key.split()
        n_value = param_config[0]
        m_value = param_config[1]
        sum_number_of_nodes = 0
        sum_number_of_edges = 0
        sum_average_degree = 0
        for graph in graph_dict[param_key]:
            sum_number_of_nodes += graph.number_of_nodes()
            sum_number_of_edges += graph.number_of_edges()
            sum_average_degree += calculate_average_degree(graph)

        number_of_nodes_measurement = sum_number_of_nodes / len(graph_dict[param_key])
        number_of_edges_measurement = sum_number_of_edges / len(graph_dict[param_key])
        average_degree_measurement = sum_average_degree / len(graph_dict[param_key])
        insert_datapoint(experiment_id,
                         {"n": n_value,
                          "m": m_value,
                          "number_of_nodes": round(number_of_nodes_measurement),
                          "number_of_edges": round(number_of_edges_measurement),
                          "average_degree": average_degree_measurement},
                         "thesis_nicola")

        # logging
        print(f"added point for parameter configuration {param_key}")


def calculate_properties(graph_dict: dict, experiment_id: ObjectId):
    for param_key in graph_dict:
        param_config = param_key.split()
        ple_value = param_config[0]
        t_value = param_config[1]
        sum_number_of_nodes = 0
        sum_number_of_edges = 0
        sum_average_degree = 0
        sum_diameter = 0
        sum_heterogeneity = 0
        sum_clustering = 0
        for graph in graph_dict[param_key]:
            sum_number_of_nodes += graph.number_of_nodes()
            sum_number_of_edges += graph.number_of_edges()
            sum_average_degree += calculate_average_degree(graph)
            sum_diameter += calculate_diameter_approximation(graph)
            sum_heterogeneity += calculate_heterogeneity(graph)
            sum_clustering += calculate_clustering_coefficient(graph)

        number_of_nodes_measurement = sum_number_of_nodes / len(graph_dict[param_key])
        number_of_edges_measurement = sum_number_of_edges / len(graph_dict[param_key])
        average_degree_measurement = sum_average_degree / len(graph_dict[param_key])
        diameter_measurement = sum_diameter / len(graph_dict[param_key])
        heterogeneity_measurement = sum_heterogeneity / len(graph_dict[param_key])
        clustering_measurement = sum_clustering / len(graph_dict[param_key])
        insert_datapoint(experiment_id,
                         {"power_law_exponent": ple_value,
                          "temperature": t_value,
                          "number_of_nodes": round(number_of_nodes_measurement),
                          "number_of_edges": round(number_of_edges_measurement),
                          "average_degree": average_degree_measurement,
                          "diameter": diameter_measurement,
                          "heterogeneity": heterogeneity_measurement,
                          "average_clustering": clustering_measurement},
                         "thesis_nicola")

        # logging
        print(f"added point for parameter configuration {param_key}")
