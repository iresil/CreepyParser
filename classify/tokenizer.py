import time
import re
import definitions
import spacy
import enchant
from spacytextblob.spacytextblob import SpacyTextBlob  ### Do not remove! ###
from text.outputFormatter import OutputFormatter


class Tokenizer:
    @staticmethod
    def extract_parts_analyze_sentiment(categories, stories):
        """ Extracts tokens, spans and sentiments from categories and story texts. """

        start = time.time()
        # Filter out unwanted tokens
        parts_of_speech_to_remove = ['ADV', 'PRON', 'INTJ', 'CCONJ', 'PUNCT', 'PART', 'DET', 'ADP', 'SPACE', 'NUM', 'SYM']
        print("Categories (Words):")
        category_tokens = Tokenizer.__filter_tokens(categories, parts_of_speech_to_remove, True, True, definitions.DEBUG)
        print("--- %s seconds ---" % (time.time() - start))
        start = time.time()
        print("Categories (Sentences/Sentiments):")
        category_spans, category_sentiments = Tokenizer.__filter_tokens(categories, parts_of_speech_to_remove, False, False, definitions.DEBUG)
        print("--- %s seconds ---" % (time.time() - start))
        start = time.time()
        print("Stories (Words):")
        story_tokens = Tokenizer.__filter_tokens(stories, parts_of_speech_to_remove, True, True, definitions.DEBUG)
        print("--- %s seconds ---" % (time.time() - start))
        start = time.time()
        print("Stories (Sentences/Sentiments):")
        story_spans, story_sentiments = Tokenizer.__filter_tokens(stories, parts_of_speech_to_remove, False, True, definitions.DEBUG)
        print("--- %s seconds ---" % (time.time() - start))

        return category_tokens, category_spans, category_sentiments, story_tokens, story_spans, story_sentiments

    @staticmethod
    def __filter_tokens(texts, parts_of_speech_to_remove, use_single_words, enable_ner, debug):
        """ Filters out tokens that we don't need (e.g. specific parts of speech, human names, etc.) """
        count = len(texts)
        disable_list = ['textcat']
        if not enable_ner:
            disable_list.append('ner')
        # Load english language model
        nlp = spacy.load('en_core_web_sm', disable=disable_list)
        spellchecker = enchant.Dict("en_US")

        results = []
        sentiments = []
        i = 0
        nlp.add_pipe('spacytextblob')
        docs = nlp.pipe(texts, batch_size=50)
        for doc in docs:
            if not use_single_words:
                sentiment_results = doc._.blob.sentiment_assessments.assessments
                sents = []
                for sent in sentiment_results:
                    sents.append(' '.join(sent[0]) + ", Polarity: " + str(sent[1]) + ", Subjectivity: " + str(sent[2]))
                sentiments.append(sorted(list(set(sents))))

            if enable_ner:
                words_to_remove = [token.text for token in doc
                                   if token.pos_ in parts_of_speech_to_remove or bool(re.search(r'\d', token.text))
                                   or not spellchecker.check(token.text)]
                words_to_remove += [span.text for span in doc.ents
                                    if span.label_ == "PERSON"]
                if debug:
                    print("Removable words: [" + " ".join(set(words_to_remove)) + "]")
                words_to_remove += [token.text for token in doc
                                    if token.is_stop or not token.is_alpha]
                if use_single_words:
                    words_to_keep = [token.lemma_.lower() for token in doc
                                     if token.text not in words_to_remove]
                else:
                    words_to_keep = [span.lemma_.lower() for span in doc.ents
                                     if span.text not in words_to_remove]
            else:
                words_to_keep = [token.lemma_.lower() for token in doc
                                 if token.pos_ not in parts_of_speech_to_remove and not token.is_stop and token.is_alpha]

            previous_percentage = round((i / count) * 100)
            i += 1
            if debug:
                print(str(i).zfill(len(str(len(texts)))) + ". [" + ", ".join(set(words_to_keep)) + "]")
            else:
                percentage = round((i / count) * 100)
                OutputFormatter.print_progress(percentage, previous_percentage)

            results.append(list(set(words_to_keep)))

        if not use_single_words:
            return results, sentiments
        else:
            return results
