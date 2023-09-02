import os
import definitions
from gensim.models import LdaMulticore
from gensim.test.utils import datapath
from database.storyItem import StoryItem
from database.tokenReader import TokenReader
from classify.textProcessor import TextProcessor
from analyze.outlierDetector import OutlierDetector


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
    __story_passes = 500

    def __init__(self, story_data: list[StoryItem], training_set=False):
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
                                                                                                    definitions.CATEGORY_KEEP_N, training_set=training_set)

        token_dist = {}
        if training_set:
            token_dist = TokenReader.get_token_distribution()
        else:
            for i in range(len(self.story_tokens)):
                for token in self.story_tokens[i]:
                    times_found = self.story_data[i].text.count(token)
                    if token not in token_dist.keys():
                        token_dist[token] = times_found
                    else:
                        token_dist[token] += times_found
        tokens_to_keep = OutlierDetector.find_clustered_tokens(token_dist)

        print("")
        print("[Filtering story tokens]")
        self.story_corpus, self.story_dictionary = TextProcessor.retrieve_filtered_dictionary(self.story_tokens, definitions.STORY_NO_ABOVE,
                                                                                              definitions.STORY_KEEP_N, tokens_to_keep, training_set)

    def train_models(self):
        """ Train two models, one for categories and one for stories, and save them to disk. """

        Classifier.__train_model(self.category_corpus, self.category_dictionary, self.__category_num_topics,
                                 self.__category_passes, "category_model")
        Classifier.__train_model(self.story_corpus, self.story_dictionary, self.__story_num_topics,
                                 self.__story_passes, "story_model")

    def make_predictions(self, training_set=False):
        """ Make predictions for the requested stories, based on categories and story content, separately. """

        self.__predict("category_model", self.category_corpus, self.category_dictionary, self.category_tokens,
                       self.__category_sentiments, training_set)
        print("-------------")
        self.__predict("story_model", self.story_corpus, self.story_dictionary, self.story_tokens,
                       self.__story_sentiments, training_set)

    @staticmethod
    def __train_model(corpus, dictionary, num_topics, passes, model_name):
        """ Train an LdaMulticore model. """

        print("")
        print("Training " + model_name + " ...")
        lda_model = LdaMulticore(corpus=corpus, id2word=dictionary, iterations=15000, num_topics=num_topics, workers=4,
                                 passes=passes, minimum_probability=0.3, decay=1, per_word_topics=True, minimum_phi_value=0.5,
                                 chunksize=100, eval_every=3)
        topics_seq = lda_model.print_topics(-1)

        print("")
        print(topics_seq)
        print("")

        model = datapath(os.path.join(definitions.RESOURCE_DIR, model_name))
        lda_model.save(model)

    def __predict(self, model_name, corpus, dictionary, tokens, sentiments, training_set):
        """ Make predictions for the requested stories, using the requested (already saved) model. """

        print("")
        print("Loading " + model_name + " from disk")
        model = datapath(os.path.join(definitions.RESOURCE_DIR, model_name))
        lda_model = LdaMulticore.load(model)

        for i in range(len(tokens)):
            prediction = lda_model[corpus][i]
            most_probable_topic = list(reversed(sorted(prediction[0], key=lambda x: x[1])))[0] if prediction[0] != [] else None
            largest_probability = round(most_probable_topic[1] * 100, 2) if most_probable_topic is not None else 0
            topic_index = most_probable_topic[0] if most_probable_topic is not None else -1
            corpus_ref = []
            if topic_index > 0:
                for j in range(len(prediction[2])):
                    token_index = prediction[2][j][0]
                    per_topic_probabilities = list(reversed(sorted(prediction[2][j][1], key=lambda x: x[1])))
                    largest_topic_probability = per_topic_probabilities[0][1] * 100 if per_topic_probabilities != [] else 0
                    first_probable_topic = per_topic_probabilities[0][0] if per_topic_probabilities != [] else -1
                    if (training_set and largest_topic_probability > 75 and first_probable_topic == topic_index)\
                            or (not training_set and largest_topic_probability >= 99.5 and first_probable_topic == topic_index):
                        corpus_ref.append(token_index)

            topic = ""
            for j in range(len(corpus_ref)):
                token_index = corpus_ref[j]
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
