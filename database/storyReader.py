import definitions
import mysql.connector
from database.storyItem import StoryItem


class StoryReader:
    """ Retrieves story data from the DB. """

    @staticmethod
    def get_stories():
        """ Attempts to retrieve all stories from the DB. """

        story_items = []
        sql = "SELECT * FROM stories ORDER BY rating DESC"

        records, row_count = StoryReader.__select_data(sql)
        if row_count > 0:
            print("Total number of stories in table: ", row_count)

            for row in records:
                story_item = StoryItem()
                story_item.id = row[0]
                story_item.link = row[1]
                story_item.title = row[2]
                story_item.rating = row[3]
                story_item.reading_time = row[4]
                story_item.categories = row[5].strip('["').strip('"]').split('", "')
                story_item.text = ' '.join(row[6].strip('["').strip('"]').split('", "')).encode("utf-8").decode("unicode-escape")
                story_items.append(story_item)

        return story_items

    @staticmethod
    def get_unprocessed(story_items: list[StoryItem]):
        """
        Filters out StoryItems from the input list, if they've already been processed.
        Returns a second list with partially processed StoryItems (i.e. the ones for which token, span or sentiment
        storage didn't finish).
        """

        token_count = StoryReader.__get_token_count()
        span_count = StoryReader.__get_span_count()
        sentiment_count = StoryReader.__get_sentiment_count()

        processed = []
        half_processed = []
        for si in story_items:
            for tc in token_count:
                if (tc[0] == si.id and tc[1] == 'CAT' and tc[2] == len(si.category_tokens))\
                        or (tc[0] == si.id and tc[1] == 'TXT' and tc[2] == len(si.story_tokens)):
                    processed.append(si)
                elif (tc[0] == si.id and tc[1] == 'CAT' and tc[2] != len(si.category_tokens))\
                        or (tc[0] == si.id and tc[1] == 'TXT' and tc[2] != len(si.story_tokens)):
                    half_processed.append(si)
                    if si in processed:
                        processed.remove(si)

            for sc in span_count:
                if (sc[0] == si.id and sc[1] == 'CAT' and sc[2] == len(si.category_spans))\
                        or (sc[0] == si.id and sc[1] == 'TXT' and sc[2] == len(si.story_spans)):
                    processed.append(si)
                elif (sc[0] == si.id and sc[1] == 'CAT' and sc[2] != len(si.category_spans))\
                        or (sc[0] == si.id and sc[1] == 'TXT' and sc[2] != len(si.story_spans)):
                    half_processed.append(si)
                    if si in processed:
                        processed.remove(si)

            for sc in sentiment_count:
                if (sc[0] == si.id and sc[1] == 'CAT' and sc[2] == len(si.category_sentiments))\
                        or (sc[0] == si.id and sc[1] == 'TXT' and sc[2] == len(si.story_sentiments)):
                    processed.append(si)
                elif (sc[0] == si.id and sc[1] == 'CAT' and sc[2] != len(si.category_sentiments))\
                        or (sc[0] == si.id and sc[1] == 'TXT' and sc[2] != len(si.story_sentiments)):
                    half_processed.append(si)
                    if si in processed:
                        processed.remove(si)

        processed = list(set(processed))
        half_processed = list(set(half_processed))

        for itm in processed:
            if itm in story_items:
                story_items.remove(itm)
        for itm in half_processed:
            if itm in story_items:
                story_items.remove(itm)

        return half_processed

    @staticmethod
    def __get_token_count():
        """ Retrieves the total number of stored tokens per story and source. """

        token_count = []
        sql = "SELECT story_id, source, COUNT(token) AS token_count FROM tokens GROUP BY story_id, source;"

        records, row_count = StoryReader.__select_data(sql)
        if row_count > 0:
            print("Total number of tokens in table: ", row_count)

            for row in records:
                result = [row[0], row[1], row[2]]
                token_count.append(result)

        return token_count

    @staticmethod
    def __get_span_count():
        """ Retrieves the total number of stored spans per story and source. """

        span_count = []
        sql = "SELECT story_id, source, COUNT(span) AS span_count FROM spans GROUP BY story_id, source;"

        records, row_count = StoryReader.__select_data(sql)
        if row_count > 0:
            print("Total number of spans in table: ", row_count)

            for row in records:
                result = [row[0], row[1], row[2]]
                span_count.append(result)

        return span_count

    @staticmethod
    def __get_sentiment_count():
        """ Retrieves the total number of stored sentiments per story and source. """

        sentiment_count = []
        sql = "SELECT story_id, source, COUNT(text) AS text_count FROM sentiments GROUP BY story_id, source;"

        records, row_count = StoryReader.__select_data(sql)
        if row_count > 0:
            print("Total number of sentiments in table: ", row_count)

            for row in records:
                result = [row[0], row[1], row[2]]
                sentiment_count.append(result)

        return sentiment_count

    @staticmethod
    def __select_data(sql):
        """ Retrieves data from the database, using the provided query. """
        row_count = 0
        records = []
        try:
            connection = mysql.connector.connect(host=definitions.MYSQL_HOST, database=definitions.MYSQL_DB,
                                                 user=definitions.MYSQL_USER,
                                                 password=definitions.MYSQL_PASSWORD,
                                                 use_unicode=True, charset='utf8',
                                                 init_command='SET NAMES UTF8')

            cursor = connection.cursor()
            cursor.execute(sql)
            records = cursor.fetchall()
            row_count = cursor.rowcount
        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if connection.is_connected():
                connection.close()
                cursor.close()

        return records, row_count
