import nltk
import json
from nltk.corpus import wordnet
from pymongo import MongoClient
from nltk import pos_tag
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download("wordnet")


class offer_class():

    def __init__(self, offer):

        self.text = None
        self.description = offer[1]["description"] #just this for starters.
        self.raw_text = self.description
        self.ID = offer[1]["listing_url"]
        self.tagged = None
        self.timestamp = None
        self.parameter_dict = {}
        client = MongoClient()  # database stuff
        self.db = client.prototype

    def preprocess(self):
        """
        apply nlp preprocessing steps to ensure proper structure of data
        :return:
        """

        # translate to target language here - we can recognise different languages in the recognise_google function

        # remove stop words - these are typically not important - we lose negations though :/ lets not do that for the moment

        # words should be transformed into tokens to work with in nlp
        assert (self.raw_text is not None), "words must be detectable"
        self.text = word_tokenize(self.raw_text)

        # we need to address the part of speech tag for later wordnet usage
        try:
            self.tagged = pos_tag(self.text)
        except:
            self.tagged = None
            print("non-understandable text")

        # we will lowercase them all to make them comparable and matchable

        assert (self.text is not None), "text may not be none"
        assert (self.tagged is not None), "tagged words may not be none"
        self.text = [token.lower() for token in self.text]
        self.data = self.text

        return

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
                            print("added element is", element)
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
