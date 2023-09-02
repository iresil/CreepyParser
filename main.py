import os
import json
import definitions
from database.storyItem import StoryItem
from database.storyReader import StoryReader
from classify.textProcessor import TextProcessor
from analyze.coherenceCalculator import CoherenceCalculator
from database.tokenReader import TokenReader
from classify.classifier import Classifier


if __name__ == '__main__':
    if definitions.MINE_TEXT:
        story_data = StoryReader.get_stories()
        TextProcessor.mine_text(story_data, True)

    if definitions.CATEGORY_COHERENCE or definitions.STORY_COHERENCE or definitions.TRAIN_MODELS:
        story_items = TokenReader.get_all()
        if definitions.CATEGORY_COHERENCE:
            print("[Coherence calculation based on categories starting]")
            CoherenceCalculator.calculate_cat(story_items)
        if definitions.STORY_COHERENCE:
            print("[Coherence calculation based on stories starting]")
            CoherenceCalculator.calculate_txt(story_items)

        if definitions.TRAIN_MODELS:
            classifier = Classifier(story_items, True)
            classifier.train_models()
        if definitions.TEST_PREDICTIONS:
            classifier = Classifier(story_items)
            classifier.make_predictions()

    f = open(os.path.join(definitions.RESOURCE_DIR, 'story_sample.json'), 'r')
    data = f.read()
    f.close()
    stories_to_test = [StoryItem(data)]
    TextProcessor.mine_text(stories_to_test)

    classifier = Classifier(stories_to_test)
    classifier.make_predictions()
