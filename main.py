from start import init_data
from analyse import analyse_data
from helper import set_up_mongodb, add_data

set_up_mongodb()
search_selected = None

# ask user whether to search or contribute
print("reached this point in main.py")
user_choice = input("Would you like to search [S] or contribute [C]: \n")
if user_choice == 'S':
    search_selected = True
else:
    search_selected = False

if search_selected == True:
    init_data = init_data()
    init_data.recognise_input()
    init_data.import_input()
    init_data.preprocess()

    analyse_data = analyse_data(init_data)
    best_matches = analyse_data.check()
    print(best_matches)

if search_selected == False:
    add_data()

"""
Ideas:
track where people click
analyse text and check what kind of parameters people are still missing?
"""

