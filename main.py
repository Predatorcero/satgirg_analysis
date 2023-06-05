from bson import ObjectId
from property_calculation import get_vertices_edges_graph_chunks, get_ple_temperature_graph_chunks, calculate_basic_properties, calculate_properties
from database_setup import insert_experiment_to_db, insert_datapoint, experiments_for_platform, data_from_experiment, \
    delete_experiment_from_db


if __name__ == '__main__':
    # WARNING: FOR DELETE ONLY
    # delete_experiment_from_db("test-uniform-weight-satgirg-properties", "thesis_nicola")

    # to get experiments of a database
    # experiments_df = experiments_for_platform("thesis_nicola")

    # to observe content of one experiment id (of a database)
    # data = data_from_experiment(ObjectId("647bb63671dc6ba30fc0a8a9"), "thesis_nicola")

    # CSV GENERATION EXAMPLE

    # to get chunked graphs
    # ple_temperature_graph_chunks = get_ple_temperature_graph_chunks("power_law_temperature_graphs/uniform_weights_various_temperature_satgirgs")
    vertices_edges_graph_chunks = get_vertices_edges_graph_chunks("vertices_edges_graphs/ple=inf_t=0_satgirgs")

    # to insert an experiment for a database
    experiment_id = insert_experiment_to_db("uniform-weight-temperature-satgirg-properties", "thesis_nicola")

    # to insert data into an experiment
    calculate_basic_properties(vertices_edges_graph_chunks, experiment_id)
