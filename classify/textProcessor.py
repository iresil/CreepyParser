from database.storyItem import StoryItem
from database.storyReader import StoryReader
from database.storyWriter import StoryWriter
from classify.tokenizer import Tokenizer


class TextProcessor:
    @staticmethod
    def mine_text(story_data: list[StoryItem]):
        stories = []
        categories = []
        for sd in story_data:
            stories.append(sd.text.lower())
            categories.append((', '.join(sd.categories)).lower())

        category_tokens, category_spans, category_sentiments, story_tokens, story_spans, story_sentiments =\
            Tokenizer.extract_parts_analyze_sentiment(categories, stories)

        for i in range(len(story_data)):
            story_data[i].add_tokenizer_result(category_tokens[i], category_spans[i], category_sentiments[i],
                                               story_tokens[i], story_spans[i], story_sentiments[i])

        half_processed = StoryReader.get_unprocessed(story_data)

        story_writer = StoryWriter()
        story_writer.insert_remaining_items(half_processed, story_data)
