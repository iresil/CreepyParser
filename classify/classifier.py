import os
import definitions
from gensim.models import LdaMulticore
from gensim.test.utils import datapath
from database.storyItem import StoryItem
from classify.textProcessor import TextProcessor


class Classifier:
    """ Manages model training and predictions for classification purposes. """

    story_data = []

    category_tokens = []
    story_tokens = []

    category_corpus = None
    category_dictionary = None
    story_corpus = None
    story_dictionary = None

    __category_sentiments = []
    __category_num_topics = 5
    __category_passes = 1000
    __story_sentiments = []
    __story_num_topics = 3
    __story_passes = 50

    def __init__(self, story_data: list[StoryItem]):
        """ Prepares the classifier for training or predictions. """

        self.story_data = story_data
        self.category_tokens = []
        self.story_tokens = []
        self.__category_sentiments = []
        self.__story_sentiments = []
        for sd in self.story_data:
            self.category_tokens.append(sd.category_tokens)
            self.story_tokens.append(sd.story_tokens)
            self.__category_sentiments.append(sd.category_sentiments)
            self.__story_sentiments.append(sd.story_sentiments)

        print("")
        print("[Filtering category tokens]")
        self.category_corpus, self.category_dictionary = TextProcessor.retrieve_filtered_dictionary(self.category_tokens, definitions.CATEGORY_NO_ABOVE,
                                                                                                    definitions.CATEGORY_KEEP_N)
        print("")
        print("[Filtering story tokens]")
        self.story_corpus, self.story_dictionary = TextProcessor.retrieve_filtered_dictionary(self.story_tokens, definitions.STORY_NO_ABOVE,
                                                                                              definitions.STORY_KEEP_N)

    def train_models(self):
        """ Train two models, one for categories and one for stories, and save them to disk. """

        Classifier.__train_model(self.category_corpus, self.category_dictionary, self.__category_num_topics,
                                 self.__category_passes, "category_model")
        Classifier.__train_model(self.story_corpus, self.story_dictionary, self.__story_num_topics,
                                 self.__story_passes, "story_model")

    def make_predictions(self):
        """ Make predictions for the requested stories, based on categories and story content, separately. """

        self.__predict("category_model", self.category_corpus, self.category_dictionary, self.category_tokens, self.__category_sentiments)
        print("-------------")
        self.__predict("story_model", self.story_corpus, self.story_dictionary, self.story_tokens, self.__story_sentiments)

    @staticmethod
    def __train_model(corpus, dictionary, num_topics, passes, model_name):
        """ Train an LdaMulticore model. """

        print("")
        print("Training " + model_name + " ...")
        lda_model = LdaMulticore(corpus=corpus, id2word=dictionary, iterations=1000, num_topics=num_topics, workers=4,
                                 passes=passes)
        topics_seq = lda_model.print_topics(-1)

        print("")
        print(topics_seq)
        print("")

        model = datapath(os.path.join(definitions.SAVED_MODEL_DIR, model_name))
        lda_model.save(model)

    def __predict(self, model_name, corpus, dictionary, tokens, sentiments):
        """ Make predictions for the requested stories, using the requested (already saved) model. """

        print("")
        print("Loading " + model_name + " from disk")
        model = datapath(os.path.join(definitions.SAVED_MODEL_DIR, model_name))
        lda_model = LdaMulticore.load(model)

        for i in range(len(tokens)):
            probabilities = lda_model[corpus][i]
            probabilities_sorted = sorted(probabilities, key=lambda x: x[1])
            largest_probability = round(reversed(probabilities_sorted).__next__()[1] * 100,
                                        2) if probabilities_sorted != [] else 0
            largest_probability_index = reversed(probabilities_sorted).__next__()[
                                            0] - 1 if probabilities_sorted != [] else None
            corpus_ref = corpus[largest_probability_index] if largest_probability_index is not None else []

            topic = ""
            for j in range(len(corpus_ref)):
                token_index = corpus_ref[j][0]
                token_txt = dictionary[token_index]  # dictionary.id2token[] won't work here, because it's populated on request
                topic += (", " if topic != "" else "") + token_txt

            self.story_data[i].probability = largest_probability
            self.story_data[i].topic = topic
            if "story" in model_name:
                self.story_data[i].story_tokens = tokens[i]
                self.story_data[i].story_sentiments = sentiments[i]
            else:
                self.story_data[i].category_tokens = tokens[i]
                self.story_data[i].category_sentiments = sentiments[i]

            self.story_data[i].print()
