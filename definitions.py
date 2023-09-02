import os

DEBUG = False

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(ROOT_DIR, 'resources')

MYSQL_HOST = 'localhost'
MYSQL_USER = 'python'
MYSQL_PASSWORD = 'python'
MYSQL_DB = 'creepystore'

MINE_TEXT = False
CATEGORY_COHERENCE = False
STORY_COHERENCE = False
TRAIN_MODELS = False
TEST_PREDICTIONS = False

CATEGORY_NO_ABOVE = 0.7
CATEGORY_KEEP_N = 50
STORY_NO_ABOVE = 0.3
STORY_KEEP_N = 1000

MIN_PROBABILITY_PER_WORD = 99.5
