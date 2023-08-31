import time
import matplotlib.pyplot as plt
from gensim.models import LdaMulticore
from gensim.models import CoherenceModel
from database.storyItem import StoryItem
from classify.textProcessor import TextProcessor


class CoherenceCalculator:
    """ Determines the best configuration for LdaMulticore, based on coherence scores. """

    @staticmethod
    def calculate_cat(story_data: list[StoryItem]):
        """
        Sequentially plots coherence scores vs. number of topics (extracted from categories),
        using either C_umass or C_v, to determine what the best configuration for LdaMulticore is.
        """

        category_tokens = []
        for sd in story_data:
            category_tokens.append(sd.category_tokens)

        corpus, dictionary = TextProcessor.retrieve_filtered_dictionary(category_tokens)
        CoherenceCalculator.__c_umass(corpus, dictionary)
        CoherenceCalculator.__c_v(corpus, dictionary, category_tokens)

    @staticmethod
    def calculate_txt(story_data: list[StoryItem]):
        """
        Sequentially plots coherence scores vs. number of topics (extracted from categories),
        using either C_umass or C_v, to determine what the best configuration for LdaMulticore is.
        """

        story_tokens = []
        for sd in story_data:
            story_tokens.append(sd.story_tokens)

        corpus, dictionary = TextProcessor.retrieve_filtered_dictionary(story_tokens)
        CoherenceCalculator.__c_umass(corpus, dictionary)
        CoherenceCalculator.__c_v(corpus, dictionary, story_tokens)

    @staticmethod
    def __c_umass(corpus, dictionary):
        """
        Performs multiple attempts to extract an amount of topics, ranging from 1 to 20, from the corpus.
        Calculates coherence using C_umass and displays the resulting plot.
        """

        topics = []
        score = []
        for i in range(1, 20, 1):
            print("Attempting to train with num_topics=%s" % i)
            start = time.time()
            lda_model = LdaMulticore(corpus=corpus, id2word=dictionary, iterations=10,
                                     num_topics=i, workers=4, passes=50, random_state=100)
            print("--- %s seconds ---" % (time.time() - start))

            print("Calculating coherence for num_topics=%s" % i)
            start = time.time()
            cm = CoherenceModel(model=lda_model, corpus=corpus, dictionary=dictionary, coherence='u_mass')
            print("--- %s seconds ---" % (time.time() - start))

            topics.append(i)
            score.append(cm.get_coherence())

        _ = plt.plot(topics, score)
        _ = plt.xlabel('Number of Topics')
        _ = plt.ylabel('Coherence Score')
        plt.show()

    @staticmethod
    def __c_v(corpus, dictionary, tokens):
        """
        Performs multiple attempts to extract an amount of topics, ranging from 1 to 20, from the corpus.
        Calculates coherence using C_v and displays the resulting plot.
        """

        topics = []
        score = []
        for i in range(1, 20, 1):
            print("Attempting to train with num_topics=%s" % i)
            start = time.time()
            lda_model = LdaMulticore(corpus=corpus, id2word=dictionary, iterations=10,
                                     num_topics=i, workers=4, passes=50, random_state=100)
            print("--- %s seconds ---" % (time.time() - start))

            print("Calculating coherence for num_topics=%s" % i)
            start = time.time()
            cm = CoherenceModel(model=lda_model, texts=tokens, corpus=corpus, dictionary=dictionary, coherence='c_v')
            print("--- %s seconds ---" % (time.time() - start))

            topics.append(i)
            score.append(cm.get_coherence())

        _ = plt.plot(topics, score)
        _ = plt.xlabel('Number of Topics')
        _ = plt.ylabel('Coherence Score')
        plt.show()
