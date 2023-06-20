from bson import ObjectId
from property_calculation import get_vertices_edges_graph_chunks, get_ple_temperature_graph_chunks, calculate_diameter_approximation, calculate_basic_properties, calculate_properties
from database_setup import insert_experiment_to_db, insert_datapoint, experiments_for_platform, data_from_experiment, \
    delete_experiment_from_db


if __name__ == '__main__':
    # WARNING: FOR DELETE ONLY
    # delete_experiment_from_db("test-uniform-weight-satgirg-properties", "thesis_nicola")

    # to get experiments of a database
    experiments_df = experiments_for_platform("thesis_nicola")

    # to observe content of one experiment id (of a database)
    data = data_from_experiment(ObjectId("648f6c003895dc41b30a9d40"), "thesis_nicola")
    # CSV GENERATION EXAMPLE VERTICES EDGES

    # to get chunked graphs
    # vertices_edges_graph_chunks = get_vertices_edges_graph_chunks("vertices_edges_graphs/ple=2.4_t=0.5_satgirgs")

    # to insert an experiment for a database
    # experiment_id = insert_experiment_to_db("ple=2.4_t=0.5_satgirg_vertices_edges", "thesis_nicola")

    # to insert data into an experiment
    # calculate_basic_properties(vertices_edges_graph_chunks, experiment_id)

    # CSV GENERATION EXAMPLE OTHER PROPERTIES

    # to get chunked graphs
    ple_temperature_graph_chunks = get_ple_temperature_graph_chunks("power_law_temperature_graphs/various_ple_temperature_satgirgs")

    # to insert an experiment for a database
    experiment_id = insert_experiment_to_db("test-diameter-small-satgirgs", "thesis_nicola")

    # to insert data into an experiment
    calculate_properties(ple_temperature_graph_chunks, experiment_id)
