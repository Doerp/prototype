import speech_recognition as sr
import datetime
import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


class init_data:

    """
    used for initialising data and preprocessing tasks
    """

    def __init__(self, input = None):

        self.input = input
        self.text = None
        self.raw_text = None
        self.tagged = None
        self.timestamp = None

    def recognise_input(self):
        """
        recognise what kind of input we are getting. to be continued
        :return:
        """
        # is it live or not live?
        mode = "live"
        speech = True
        # speech = False

        self.mode = mode
        self.speech = speech

        return

    def import_input(self):
        """
        importing the input properly and deriving textual data from it
        :return:
        """

        if self.speech is True and self.mode == "live":
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Speak Anything :")
                r.adjust_for_ambient_noise(source)
                self.audio = r.listen(source)

            try:
                text = r.recognize_google(self.audio)
                print("You said : {}".format(text))
                self.raw_text = text

                # save the text for the collection in mongoDB
                self.timestamp = str(datetime.datetime.now())

                return

            except:
                print("Sorry could not recognize your voice")
                return

        else:
            text = input("Enter your search demands: ")
            self.raw_text = text
            self.audio = None
            # pass

        return

    def preprocess(self):
        """
        apply nlp preprocessing steps to ensure proper structure of data
        :return:
        """

        #translate to target language here - we can recognise different languages in the recognise_google function

        #remove stop words - these are typically not important - we lose negations though :/ lets not do that for the moment

        #words should be transformed into tokens to work with in nlp
        assert (self.raw_text is not None), "words must be detectable"
        self.text = word_tokenize(self.raw_text)

        #we need to address the part of speech tag for later wordnet usage
        try:
            self.tagged = pos_tag(self.text)
        except:
            self.tagged = None
            print("non-understandable text")

        #we will lowercase them all to make them comparable and matchable

        assert(self.text is not None), "text may not be none"
        assert(self.tagged is not None), "tagged words may not be none"
        self.text = [token.lower() for token in self.text]

        return

