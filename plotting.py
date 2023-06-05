import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_degree_distribution(g: nx.Graph):
    degrees = [g.degree(n) for n in g.nodes]
    plt.hist(degrees, list(range(1, 15)))
    plt.show()


def plot_heterogeneity_locality_difference(girg_csv: str, satgirg_csv: str):
    girg_df = pd.read_csv(girg_csv)
    satgirg_df = pd.read_csv(satgirg_csv)

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
    plt.scatter(satgirg_heterogeneity_list, satgirg_locality_list, c=satgirg_edges, label="satgirgs", cmap='viridis_r',
                marker='o')
    plt.clim(min_, max_)
    plt.colorbar().set_label('number of edges', rotation=270, labelpad=15)

    plt.xlabel("heterogeneity")
    plt.ylabel("average clustering")
    plt.legend()
    plt.show()


def plot_heterogeneity_clustering_line(girg_csv: str, satgirg_csv: str):
    girg_df = pd.read_csv(girg_csv)
    satgirg_df = pd.read_csv(satgirg_csv)
    girg_temperature_grouped = girg_df.groupby(girg_df["temperature"])
    for group in girg_temperature_grouped:
        girg_heterogeneity = group[1]["heterogeneity"]
        girg_clustering = group[1]["average_clustering"]
        plt.plot(girg_heterogeneity, girg_clustering, "-o", color="blue")

    girg_power_law_exponent_grouped = girg_df.groupby(girg_df["power_law_exponent"])
    for group in girg_power_law_exponent_grouped:
        girg_heterogeneity = group[1]["heterogeneity"]
        girg_clustering = group[1]["average_clustering"]
        plt.plot(girg_heterogeneity, girg_clustering, "-o", color="blue")

    satgirg_temperature_grouped = satgirg_df.groupby(satgirg_df["temperature"])
    for group in satgirg_temperature_grouped:
        satgirg_heterogeneity = group[1]["heterogeneity"]
        satgirg_clustering = group[1]["average_clustering"]
        plt.plot(satgirg_heterogeneity, satgirg_clustering, "-o", color="red")

    satgirg_power_law_exponent_grouped = satgirg_df.groupby(satgirg_df["power_law_exponent"])
    for group in satgirg_power_law_exponent_grouped:
        satgirg_heterogeneity = group[1]["heterogeneity"]
        satgirg_clustering = group[1]["average_clustering"]
        plt.plot(satgirg_heterogeneity, satgirg_clustering, "-o", color="red")

    plt.xlabel("heterogeneity")
    plt.ylabel("average clustering")
    plt.grid()
    plt.show()


def plot_heterogeneity_clustering_uniform_vs_various_weights_satgirg(uniform_satgirgs: str, various_satgirgs):
    uniform_satgirgs_df = pd.read_csv(uniform_satgirgs)
    various_satgirgs_df = pd.read_csv(various_satgirgs)

    various_satgirgs_heterogeneity_list = various_satgirgs_df["heterogeneity"]
    various_satgirgs_locality_list = various_satgirgs_df["average_clustering"]
    plt.scatter(various_satgirgs_heterogeneity_list, various_satgirgs_locality_list, label="all parameter configurations VGIRGs")

    uniform_satgirgs_heterogeneity_list = uniform_satgirgs_df["heterogeneity"]
    uniform_satgirgs_locality_list = uniform_satgirgs_df["average_clustering"]
    plt.scatter(uniform_satgirgs_heterogeneity_list, uniform_satgirgs_locality_list, alpha=0.7, label="uniform weights + various temperature VGIRGs")
    plt.xlabel("heterogeneity")
    plt.ylabel("average clustering")
    plt.legend()
    plt.grid()
    plt.show()


def plot_number_of_vertices_edges_relation(graphs: str):
    df = pd.read_csv(graphs)

    m_grouped = df.groupby(df["m"])
    for group in m_grouped:
        number_of_vertices = group[1]["number_of_nodes"]
        number_of_edges = group[1]["number_of_edges"]
        plt.plot(number_of_vertices, number_of_edges, "-o", color="#D3D3D3")

    n_grouped = df.groupby(df["n"])
    for group in n_grouped:
        number_of_vertices = group[1]["number_of_nodes"]
        number_of_edges = group[1]["number_of_edges"]
        plt.plot(number_of_vertices, number_of_edges, "-o")

    # plt.colorbar().set_label('number of edges', rotation=270, labelpad=15)
    plt.xlabel("number of vertices")
    plt.ylabel("number of edges")
    plt.grid()
    plt.show()


if __name__ == '__main__':
    # plot_heterogeneity_locality_difference("measurements/small_graphs_girg_properties.csv", "measurements/small_graphs_satgirg_properties.csv")
    # plot_number_of_vertices_edges_relation("measurements/small_graphs_satgirg_properties.csv")
    # plot_heterogeneity_clustering_line("measurements/small_graphs_girg_properties.csv", "measurements/small_graphs_satgirg_properties.csv")
    plot_heterogeneity_clustering_uniform_vs_various_weights_satgirg("measurements/uniform_weights_small_graphs_satgirg_properties.csv", "measurements/small_graphs_satgirg_properties.csv")
    # plot_number_of_vertices_edges_relation("measurements/satgirg_vertices_edges.csv")
