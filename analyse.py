from nltk.corpus import wordnet
import json
from pymongo import MongoClient
from helper import get_offers, doc2vec
from gensim.models.doc2vec import Doc2Vec


class analyse_data():
    """
    used for analysis of data and matching mechanism
    """

    def __init__(self, init_data):

        self.data = init_data.text #request text
        self.raw_data = init_data.raw_text #raw text as a backup
        self.parameter_dict = {} # dict to build with inferred parameters
        self.timestamp = init_data.timestamp #timestamp as unique identifier
        self.audio = init_data.audio # audio just to make sure
        self.tagged = init_data.tagged #POS tagged input
        self.mod = None #document similarity model

        client = MongoClient() #database stuff
        self.db = client.prototype
        self.best_fit = None #what we are aiming for goes here


    def parameter_matching(self, trail_lead = 3):
        """
        naive parameter matching and value extraction
        :param trail_lead: lead time you want to add for parameter elements to be detected
        :return:
        """

        #import parameter data

        self.parameters = self.db.parameters.find()

        print("Parameter matching...")

        #very inefficient but works
        for parameter in self.parameters:

            for word in self.data:

                #check the synonyms for each parameter and check for negations or digits
                #need to expand here for sure... need to add ceilings, ranges etc.
                if word in self.parameters["match"]:

                    investigate_elements = self.data[self.data.index[word]:self.data.index[word] + trail_lead]
                    investigate_elements.append(self.data[self.data.index[word]:self.data.index[word] - trail_lead])

                    negation = json.load(open('negation.json.json', 'r'))

                    for element in investigate_elements:

                        if element in negation:
                            self.parameter_dict[parameter["name"]] = False

                        if element.isdigit:
                            self.parameter_dict[parameter["name"]] = element

                        else:

                            continue

                else:

                    continue

        return

    def parameter_wordnet(self, tolerance = 0.80):
        """
        apply vectorisation of input to approximate our parameters.
        we can check how close words are to match words to our parameters
        :return:
        """

        coll = self.db.parameters.find()
        self.parameters = [elem["name"] for elem in coll]

        print("adjusting parameters...")

        #we need to transform our parameters and search input so that we can search for word similarity
        #for now these are only variations of nouns, we can do waaaay more though

        wordnet_updated_parameters = []

        for parameter in self.parameters:
            parameter = [parameter]
            parameter.append(".n.01")
            parameter = "".join(parameter)
            wordnet_updated_parameters.append(parameter)

        wordnet_input_text = []

        for tuple in self.tagged:

            #match for now only nouns
            if tuple[1] in ["NN", "NNS", "NNP", "NNPS"]:
                input_word = [tuple[0]]
                input_word.append(".n.01")
                input_word = "".join(input_word)
                wordnet_input_text.append(input_word)

            else:
                continue

        for parameter in wordnet_updated_parameters:

            for input in wordnet_input_text:

                if wordnet.synset(parameter).wup_similarity(wordnet.synset(input)) > tolerance:

                    #if we have similar words, add them to the parameter corpus
                    self.db.parameters.update_one(
                        {"name": parameter[:-5]},
                        {"$push": {"match": input[:-5]}}
                    )

                else:
                    continue

        return

    def check_params(self):
        """
        executes parameter matchine functions in the right order
        :return:
        """

        self.parameter_wordnet()
        self.parameter_matching()

        print("These are the parameters that we abstracted from your input")
        for param in self.parameter_dict:
            print(param + self.parameter_dict[param])


    def check_document_similarity(self, train_offers = True):
        """
        used to check document similarity of retreived request and existing offers
        :return:
        """

        if train_offers:

            offers = get_offers()

            text = self.data
            labels = self.timestamp
            text.append([offer["desc"] for offer in offers])
            labels.append([offer["label"] for offer in offers])

        else:

            text = self.data
            labels = self.timestamp

        mod = doc2vec(text = text, labels = labels, train_offers = train_offers)

        if train_offers:
            #get the most similar tags for our request
            self.best_fit = mod.most_similar(self.timestamp)

        else:
            req_vec = mod[self.timestamp]
            offers_mod = Doc2Vec.load('/mods/current_total_model.doc2vec')
            self.best_fit = offers_mod.most_similar(req_vec)




#TF_IDF?






