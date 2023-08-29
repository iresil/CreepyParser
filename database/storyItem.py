class StoryItem:
    """ The set of available information for each story. """

    id = None
    link = None
    title = None
    rating = None
    reading_time = None
    categories = None
    text = None
    category_tokens = None
    category_spans = None
    category_sentiments = None
    story_tokens = None
    story_spans = None
    story_sentiments = None

    def add_tokenizer_result(self, category_tokens, category_spans, category_sentiments,
                             story_tokens, story_spans, story_sentiments):
        """ Enrich the existing object with tokens, spans and sentiments. """

        self.category_tokens = category_tokens
        self.category_spans = category_spans
        self.category_sentiments = category_sentiments
        self.story_tokens = story_tokens
        self.story_spans = story_spans
        self.story_sentiments = story_sentiments
