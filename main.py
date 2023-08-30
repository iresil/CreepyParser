import definitions
from database.storyReader import StoryReader
from classify.textProcessor import TextProcessor


if __name__ == '__main__':
    if definitions.MINE_TEXT:
        story_data = StoryReader.get_stories()
        TextProcessor.mine_text(story_data)
