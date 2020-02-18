from start import init_data
from analyse import analyse_data
from helper import set_up_mongodb, add_data

set_up_mongodb()

user_choice = input("Would you like to search [S] or contribute [C]: \n")

if user_choice == 'S':
    init_data = init_data()
    init_data.recognise_input()
    init_data.import_input()
    init_data.preprocess()

    analyse_data = analyse_data(init_data)
    best_matches = analyse_data.check()
    print(best_matches)
    # best_matches_similarity = analyse_data.check_document_similarity()

else:
    add_data()

"""
Ideas:
track where people click
analyse text and check what kind of parameters people are still missing?
"""

