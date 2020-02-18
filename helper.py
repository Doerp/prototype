from pymongo import MongoClient
import json
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import pandas as pd
import csv

def set_up_mongodb():
    """
    sets up the initial mongodb with the parameters which is used in the analysis
    :return:
    """
    # per default a db gets created on localhost 27017
    # we can use this for our parameters since it is just a large dict and is suitable for any heterogeneous files
    client = MongoClient()
    db = client.prototype

    if db.parameters.count() == 0:

        # grab our premade parameters and insert them here
        parameters = json.load(open('parameter_words.json', 'r'))

        print(parameters)
        for param in parameters:
            db.parameters.insert_one(parameters[param])

    else:

        print("database exists - continue...")


def doc2vec(labels, text, train_offers = True):
    """
    function to create the model for document similarity between our request and existing offers
    we need two lists that are parallel (meaning integrity of label and words is crucial)
    training of offers needs to be done only if we get new offers in our database
    :param labels: should be the timestamp for our request and ony other identifier for offers
    :param text: should be the request input and the description of the offer
    :return: final model is returned
    """

    for i in range(len(labels)):
        doc = TaggedDocument(words=[text[i]], tags=[labels[i]])


    if train_offers == True:

        mod = Doc2Vec(alpha=0.25, min_alpha=0.025)
        mod.build_vocab(doc)
        mod.epochs = 10
        mod.train(doc, epochs=mod.epochs, total_examples=mod.corpus_count)
        mod.save('/mods/current_total_model.doc2vec')

        return mod

    elif train_offers == False:

        mod = Doc2Vec(alpha=0.25, min_alpha=0.025)
        mod.build_vocab(doc)
        mod.epochs = 10
        mod.train(doc, epochs=mod.epochs, total_examples=mod.corpus_count)
        #mod.save("/mods/tmp_request.doc2vec")

        return mod

def add_data():
    """
    add data to the database
    """
    new_listing_url = input("Please input listing url for new listing: ")
    new_description = input("Please input some descriptions: ")
    in_file = pd.read_csv("samples/listing_adj.csv", sep = ",", index_col=False)

    in_file.loc[-1] = [new_listing_url, new_description]  # adding a row
    in_file.index = in_file.index + 1  # shifting index
    in_file = in_file.sort_index()

    in_file.to_csv("sample/listing_adj.csv", sep = ",")


def get_offers():
    """
    retreive offers from database
    :return:
    """

    offers = pd.read_csv("samples/listing_adj.csv", sep = ",")
    return offers

if __name__ == "__main__":
    add_data()

#FINISH THIS THING UP
#testing of functions
#get offers function