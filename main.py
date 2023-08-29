from database.storyReader import StoryReader
from classify.textProcessor import TextProcessor


if __name__ == '__main__':
    # Read stories from the database
    story_data = StoryReader.get_stories()

    TextProcessor.mine_text(story_data)
