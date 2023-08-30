import definitions
from database.storyReader import StoryReader
from classify.textProcessor import TextProcessor
from analyze.coherenceCalculator import CoherenceCalculator
from database.tokenReader import TokenReader


if __name__ == '__main__':
    if definitions.MINE_TEXT:
        story_data = StoryReader.get_stories()
        TextProcessor.mine_text(story_data)

    story_items = TokenReader.get_all()
    if definitions.CATEGORY_COHERENCE:
        CoherenceCalculator.calculate_cat(story_items)
    if definitions.STORY_COHERENCE:
        CoherenceCalculator.calculate_txt(story_items)
