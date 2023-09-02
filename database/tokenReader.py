import definitions
import mysql.connector
from database.storyReader import StoryReader


class TokenReader:
    """ Retrieves tokenized story data from the DB. """

    @staticmethod
    def get_all():
        story_items = StoryReader.get_stories()
        tokens = TokenReader.__get_tokens()
        spans = TokenReader.__get_spans()
        sentiments = TokenReader.__get_sentiments()

        for si in story_items:
            si.category_tokens = []
            si.story_tokens = []
            for tc in tokens:
                if tc[0] == si.id and tc[1] == 'CAT':
                    si.category_tokens.extend(tc[2].split(','))
                elif tc[0] == si.id and tc[1] == 'TXT':
                    si.story_tokens.extend(tc[2].split(','))

            si.category_spans = []
            si.story_spans = []
            for sc in spans:
                if sc[0] == si.id and sc[1] == 'CAT':
                    si.category_spans.extend(sc[2].split(','))
                elif sc[0] == si.id and sc[1] == 'TXT':
                    si.story_spans.extend(sc[2].split(','))

            si.category_sentiments = []
            si.story_sentiments = []
            for sc in sentiments:
                if sc[0] == si.id and sc[1] == 'CAT':
                    si.category_sentiments.extend(sc[2].split(' | '))
                elif sc[0] == si.id and sc[1] == 'TXT':
                    si.story_sentiments.extend(sc[2].split(' | '))

        return story_items

    @staticmethod
    def get_token_distribution():
        """ Counts how many times each token appears in the stories. """

        token_count = {}
        sql = """
            SELECT token, count(*) total_count
            FROM tokens
            WHERE source = 'TXT'
            GROUP BY token;
        """

        records, row_count = TokenReader.__select_data(sql)
        if row_count > 0:
            print("Total counted tokens in table: ", row_count)

            for row in records:
                token_count[row[0]] = row[1]

        return token_count

    @staticmethod
    def __get_tokens():
        """ Retrieves the total number of stored tokens per story and source. """

        token_count = []
        sql = """
            SELECT story_id, source, GROUP_CONCAT(token SEPARATOR ',') AS token
            FROM tokens
            GROUP BY story_id, source;
        """

        records, row_count = TokenReader.__select_data(sql)
        if row_count > 0:
            print("Total number of grouped tokens in table: ", row_count)

            for row in records:
                result = [row[0], row[1], row[2]]
                token_count.append(result)

        return token_count

    @staticmethod
    def __get_spans():
        """ Retrieves the total number of stored spans per story and source. """

        span_count = []
        sql = """
            SELECT story_id, source, GROUP_CONCAT(span SEPARATOR ',') AS span
            FROM spans
            GROUP BY story_id, source;
        """

        records, row_count = TokenReader.__select_data(sql)
        if row_count > 0:
            print("Total number of grouped spans in table: ", row_count)

            for row in records:
                result = [row[0], row[1], row[2]]
                span_count.append(result)

        return span_count

    @staticmethod
    def __get_sentiments():
        """ Retrieves the total number of stored sentiments per story and source. """

        sentiment_count = []
        sql = """
            SELECT story_id, source,
                   GROUP_CONCAT(DISTINCT CONCAT(text, ', Polarity: ', polarity, ', Subjectivity: ', subjectivity)  SEPARATOR' | ')
            FROM sentiments
            GROUP BY story_id, source;
        """

        records, row_count = TokenReader.__select_data(sql)
        if row_count > 0:
            print("Total number of grouped sentiments in table: ", row_count)

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
                                                 init_command='SET SESSION group_concat_max_len = 1000000;')

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
