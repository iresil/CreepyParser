import definitions
import re
import mysql.connector
from database.storyItem import StoryItem
from text.outputFormatter import OutputFormatter


class StoryWriter:
    """ Stores story data to the DB. """

    def __init__(self):
        """ Initializes the connection and creates the necessary tables if they don't exist. """

        self.conn = mysql.connector.connect(
            host=definitions.MYSQL_HOST,
            user=definitions.MYSQL_USER,
            password=definitions.MYSQL_PASSWORD,
            database=definitions.MYSQL_DB
        )

        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                id INT NOT NULL auto_increment,
                story_id INT NOT NULL,
                source NVARCHAR(3) NOT NULL,
                token NVARCHAR(500) NOT NULL,
                PRIMARY KEY (id),
                UNIQUE KEY token_idx (story_id, source, token)
            );
        """)
        self.cur.close()

        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS spans (
                id INT NOT NULL auto_increment,
                story_id INT NOT NULL,
                source NVARCHAR(3) NOT NULL,
                span NVARCHAR(500) NOT NULL,
                PRIMARY KEY (id),
                UNIQUE KEY span_idx (story_id, source, span)
            );
        """)
        self.cur.close()

        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sentiments (
                id INT NOT NULL auto_increment,
                story_id INT NOT NULL,
                source NVARCHAR(3) NOT NULL,
                text NVARCHAR(500) NOT NULL,
                polarity DECIMAL(20,17),
                subjectivity DECIMAL(20,17),
                PRIMARY KEY (id),
                UNIQUE KEY sent_idx (story_id, source, text)
            );
        """)
        self.cur.close()

    def insert_remaining_items(self, half_processed, unprocessed):
        """ Inserts half-processed items row by row and unprocessed items in batches. """
        print("")
        print("Inserting data for " + str(len(half_processed)) + " half-processed stories ...")
        previous_percentage = 0
        for i in range(len(half_processed)):
            percentage = round((i / len(half_processed)) * 100)
            OutputFormatter.print_progress(percentage, previous_percentage)
            previous_percentage = round((i / len(half_processed)) * 100)

            self.insert_item(half_processed[i])
        self.close_connection()

        print("")
        print("Inserting data for " + str(len(unprocessed)) + " unprocessed stories ...")
        previous_percentage = 0
        for i in range(len(unprocessed)):
            percentage = round((i / len(unprocessed)) * 100)
            OutputFormatter.print_progress(percentage, previous_percentage)
            previous_percentage = round((i / len(unprocessed)) * 100)

            self.batch_insert_item(unprocessed[i])
        self.close_connection()

    def batch_insert_item(self, item: StoryItem):
        """ Inserts story data in batches. """

        self.__batch_insert_tokens(item)
        self.__batch_insert_spans(item)
        self.__batch_insert_sentiments(item)

    def __batch_insert_tokens(self, item: StoryItem):
        """ Inserts tokens in batches. """

        if item.category_tokens is not None and len(item.category_tokens) > 0:
            sql = "INSERT INTO tokens (story_id, source, token) VALUES "
            for i in range(len(item.category_tokens)):
                sql += ("," if i > 0 else "") + "(" + str(item.id) + ",'CAT','" + str(item.category_tokens[i]).replace("'", "") + "')"
            sql += " ON DUPLICATE KEY UPDATE story_id=story_id"
            self.__batch_insert(sql)
        if item.story_tokens is not None and len(item.story_tokens) > 0:
            sql = "INSERT INTO tokens (story_id, source, token) VALUES "
            for i in range(len(item.story_tokens)):
                sql += ("," if i > 0 else "") + "(" + str(item.id) + ",'TXT','" + str(item.story_tokens[i]).replace("'", "") + "')"
            sql += " ON DUPLICATE KEY UPDATE story_id=story_id"
            self.__batch_insert(sql)

    def __batch_insert_spans(self, item: StoryItem):
        """ Inserts spans in batches. """

        if item.category_spans is not None and len(item.category_spans) > 0:
            sql = "INSERT INTO spans (story_id, source, span) VALUES "
            for i in range(len(item.category_spans)):
                sql += ("," if i > 0 else "") + "(" + str(item.id) + ",'CAT','" + str(item.category_spans[i]).replace("'", "") + "')"
            sql += " ON DUPLICATE KEY UPDATE story_id=story_id"
            self.__batch_insert(sql)
        if item.story_spans is not None and len(item.story_spans) > 0:
            sql = "INSERT INTO spans (story_id, source, span) VALUES "
            for i in range(len(item.story_spans)):
                sql += ("," if i > 0 else "") + "(" + str(item.id) + ",'TXT','" + str(item.story_spans[i]).replace("'", "") + "')"
            sql += " ON DUPLICATE KEY UPDATE story_id=story_id"
            self.__batch_insert(sql)

    def __batch_insert_sentiments(self, item: StoryItem):
        """ Inserts sentiments in batches. """

        if item.category_sentiments is not None and len(item.category_sentiments) > 0:
            sql = "INSERT INTO sentiments (story_id, source, text, polarity, subjectivity) VALUES "
            for i in range(len(item.category_sentiments)):
                txt = re.search('(.*), Polarity', item.category_sentiments[i]).group(1).replace("'", "")
                polarity = float(re.search(', Polarity: (.*),', item.category_sentiments[i]).group(1))
                subjectivity = float(re.search(', Subjectivity: (.*)', item.category_sentiments[i]).group(1))
                sql += ("," if i > 0 else "") + "(" + str(item.id) + ",'CAT','" + txt + "'," + str(polarity) + "," + str(subjectivity) + ")"
            sql += " ON DUPLICATE KEY UPDATE story_id=story_id"
            self.__batch_insert(sql)
        if item.story_sentiments is not None and len(item.story_sentiments) > 0:
            sql = "INSERT INTO sentiments (story_id, source, text, polarity, subjectivity) VALUES "
            for i in range(len(item.story_sentiments)):
                txt = re.search('(.*), Polarity', item.story_sentiments[i]).group(1).replace("'", "")
                polarity = float(re.search(', Polarity: (.*),', item.story_sentiments[i]).group(1))
                subjectivity = float(re.search(', Subjectivity: (.*)', item.story_sentiments[i]).group(1))
                sql += ("," if i > 0 else "") + "(" + str(item.id) + ",'TXT','" + txt + "'," + str(polarity) + "," + str(subjectivity) + ")"
            sql += " ON DUPLICATE KEY UPDATE story_id=story_id"
            self.__batch_insert(sql)

    def __batch_insert(self, sql):
        """ Inserts story data in batches, using the provided query. """

        self.cur = self.conn.cursor()
        self.cur.execute(sql)
        self.conn.commit()

    def insert_item(self, item: StoryItem):
        """ Inserts story data, one row at a time. """

        self.__insert_tokens(item)
        self.__insert_spans(item)
        self.__insert_sentiments(item)

    def __insert_tokens(self, item: StoryItem):
        """ Inserts tokens, one row at a time. """

        if item.category_tokens is not None:
            for cat_token in item.category_tokens:
                self.__insert_token(item.id, 'CAT', cat_token)
        if item.story_tokens is not None:
            for txt_token in item.story_tokens:
                self.__insert_token(item.id, 'TXT', txt_token)

    def __insert_token(self, story_id, source, token):
        """ Inserts a single token row. """

        # Check to see if data is already in database
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT * FROM tokens WHERE story_id = %s AND source = %s AND token = %s", (story_id, source, token))
        result = self.cur.fetchone()

        # If it exists, log and continue, if it doesn't, insert it
        if result:
            if definitions.DEBUG:
                print("Item already in database - Story: " + str(story_id) + ", Source: " + source + ", Token: " + token)
        else:
            self.cur.execute(""" INSERT INTO tokens (story_id, source, token) 
                                 VALUES (%s,%s,%s)""", (
                story_id,
                source,
                token
            ))

        self.conn.commit()

    def __insert_spans(self, item: StoryItem):
        """ Inserts spans, one row at a time. """

        if item.category_spans is not None:
            for cat_span in item.category_spans:
                self.__insert_span(item.id, 'CAT', cat_span)
        if item.story_spans is not None:
            for txt_span in item.story_spans:
                self.__insert_span(item.id, 'TXT', txt_span)

    def __insert_span(self, story_id, source, span):
        """ Inserts a single span row. """

        # Check to see if data is already in database
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT * FROM spans WHERE story_id = %s AND source = %s AND span = %s", (story_id, source, span))
        result = self.cur.fetchone()

        # If it exists, log and continue, if it doesn't, insert it
        if result:
            if definitions.DEBUG:
                print("Item already in database - Story: " + str(story_id) + ", Source: " + source + ", Span: " + span)
        else:
            self.cur.execute(""" INSERT INTO spans (story_id, source, span) 
                                 VALUES (%s,%s,%s)""", (
                story_id,
                source,
                span
            ))

        self.conn.commit()

    def __insert_sentiments(self, item: StoryItem):
        """ Inserts sentiments, one row at a time. """

        if item.category_sentiments is not None:
            for cat_sent in item.category_sentiments:
                txt = re.search('(.*), Polarity', cat_sent).group(1)
                polarity = float(re.search(', Polarity: (.*),', cat_sent).group(1))
                subjectivity = float(re.search(', Subjectivity: (.*)', cat_sent).group(1))
                self.__insert_sentiment(item.id, 'CAT', txt, polarity, subjectivity)
        if item.story_sentiments is not None:
            for txt_sent in item.story_sentiments:
                txt = re.search('(.*), Polarity', txt_sent).group(1)
                polarity = float(re.search(', Polarity: (.*),', txt_sent).group(1))
                subjectivity = float(re.search(', Subjectivity: (.*)', txt_sent).group(1))
                self.__insert_sentiment(item.id, 'TXT', txt, polarity, subjectivity)

    def __insert_sentiment(self, story_id, source, sentiment, polarity, subjectivity):
        """ Inserts a single sentiment row. """

        # Check to see if data is already in database
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT * FROM sentiments WHERE story_id = %s AND source = %s AND text = %s",
                         (story_id, source, sentiment))
        result = self.cur.fetchone()

        # If it exists, log and continue, if it doesn't, insert it
        if result:
            if definitions.DEBUG:
                print("Item already in database - Story: " + str(story_id) + ", Source: " + source + ", Sentiment: " + sentiment)
        else:
            self.cur.execute(""" INSERT INTO sentiments (story_id, source, text, polarity, subjectivity) 
                                 VALUES (%s,%s,%s,%s,%s)""", (
                story_id,
                source,
                sentiment,
                polarity,
                subjectivity
            ))

        self.conn.commit()

    def close_connection(self):
        """ Gracefully closes the cursor and the connection. """

        self.cur.close()
        self.conn.close()
