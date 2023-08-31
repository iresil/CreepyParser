import definitions
from database.storyReader import StoryReader
from classify.textProcessor import TextProcessor
from analyze.coherenceCalculator import CoherenceCalculator
from database.tokenReader import TokenReader
from classify.classifier import Classifier


if __name__ == '__main__':
    if definitions.MINE_TEXT:
        story_data = StoryReader.get_stories()
        TextProcessor.mine_text(story_data)

    story_items = TokenReader.get_all()
    if definitions.CATEGORY_COHERENCE:
        print("[Coherence calculation based on categories starting]")
        CoherenceCalculator.calculate_cat(story_items)
    if definitions.STORY_COHERENCE:
        print("[Coherence calculation based on stories starting]")
        CoherenceCalculator.calculate_txt(story_items)

    if definitions.TRAIN_MODELS:
        classifier = Classifier(story_items)
        classifier.train_models()
    if definitions.MAKE_PREDICTIONS:
        classifier = Classifier(story_items)
        classifier.make_predictions()
