from nltk.corpus import wordnet
import json
import nltk
from pymongo import MongoClient
from helper import get_offers, doc2vec
from gensim.models.doc2vec import Doc2Vec
from offer_data import offer_class


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
        self.offer_dict = {}

        client = MongoClient() #database stuff
        self.db = client.prototype

        if self.data is None:
            print("non-workable data")
            return


    def parameter_matching(self, trail_lead = 5):
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
                if word in parameter["match"]:

                    #TODO find more adaptive way of filtering the important information
                    investigate_elements = self.data[self.data.index(word):self.data.index(word) + trail_lead]
                    investigate_elements.append(self.data[self.data.index(word):self.data.index(word) - trail_lead])

                    negation = json.load(open('negation.json', 'r'))

                    for element in investigate_elements:

                        if len(element) > 0 and len(element) < 2 and element in negation:
                            self.parameter_dict[parameter["name"]] = False
                            break

                        if len(element) > 0 and len(element) < 2 and element.isdigit():
                            self.parameter_dict[parameter["name"]] = element
                            break

                        if len(element) > 0 and len(element) < 2 and element == "close":
                            self.parameter_dict[parameter["name"]] = "close"

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

        nltk.download("wordnet")

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

                try:
                    if wordnet.synset(parameter).wup_similarity(wordnet.synset(input)) > tolerance:
                        # if we have similar words, add them to the parameter corpus
                        self.db.parameters.update_one(
                            {"name": parameter[:-5]},
                            {"$push": {"match": input[:-5]}}
                        )
                        #TODO: check for duplicates
                    else:
                        continue

                except:
                    continue

        return

    def check(self):
        """
        executes parameter matchine functions in the right order
        :return:
        """

        self.parameter_wordnet()
        self.parameter_matching() #at this points we have the parameters of the request

        #getting the parameters of the offers
        offers = get_offers()

        #for every offer perform analysis and extract parameters - then compare
        for offer_ in offers.iterrows():

            offer_ = offer_class(offer_)
            offer_.preprocess()
            offer_.parameter_wordnet()
            offer_.parameter_matching()

            try: #TODO: figure this shit out
                self.offer_dict[offer_.ID]["dict"]= offer_.parameter_dict
                self.offer_dict[offer_.ID]["score"] = 0 #initial amount of hits for the parameter setup
            except:
                continue

        #now we have the parameters of the offer and of the request based on the nlp analysis of the parameters provided
        for result in self.offer_dict["dict"]:
            for param_ in result: #if there is more than just the ID in there
                if len(param_) >1:
                    if [param_] == self.parameter_dict[param_]:
                        pass
                    else:
                        continue
                else:
                    continue

        #now we know how many matches there are between the offers and requests and can select the match with highest score
        best_matches = sorted(self.parameter_dict.items(), key=lambda x: x["score"], reverse=True)

        return best_matches

    def perform_analysis(self):
        """
        decides what analysis to perform
        document similarity only makes sense for longer descriptions for the embedding to work
        ideally we want to combine this. There are sets of strict parameters that we can use for matching and descriptions for document similarity
        """

        if len(self.data) < 100:
            self.check()

        else:
            self.check_document_similarity()


    def check_document_similarity(self, train_offers = True):
        """
        used to check document similarity of retreived request and existing offers
        still in the works
        :return:
        """

        if train_offers:

            offers = get_offers()

            text = self.data
            labels = self.timestamp
            text.append([offers["description"] for offer in offers])
            labels.append([offers["listing_url"] for offer in offers])

        else:

            text = self.data
            labels = self.timestamp

        mod = doc2vec(text = text, labels = labels, train_offers = train_offers)

        if train_offers:
            #get the most similar tags for our request
            best_fit = mod.most_similar(self.timestamp)

        else:
            req_vec = mod[self.timestamp]
            offers_mod = Doc2Vec.load('/mods/current_total_model.doc2vec')
            best_fit = offers_mod.most_similar(req_vec)

        return best_fit


#TF_IDF?






