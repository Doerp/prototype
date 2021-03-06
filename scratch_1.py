from start import init_data
from analyse import analyse_data

init_data = init_data()
init_data.recognise_input()
init_data.import_input()
init_data.preprocess()

analyse_data = analyse_data(init_data)
analyse_data.check_params()