from start import init_data
from analyse import analyse_data
from helper import set_up_mongodb

set_up_mongodb()

init_data = init_data()
init_data.recognise_input()
init_data.import_input()
init_data.preprocess()

analyse_data = analyse_data(init_data)
best_matches_parameters = analyse_data.check()
best_matches_similarity = analyse_data.check_document_similarity()

"""
Ideas:
track where people click
analyse text and check what kind of parameters people are still missing?
"""

