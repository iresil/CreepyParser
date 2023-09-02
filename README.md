# Creepy Parser
### A Python classifier for horror stories, trained on CreepyPastas
___
Simple text classifier created in **Python 3.10**, that has been trained on [CreepyPasta](https://www.creepypasta.com) stories.
Assumes you've already run [Creepy Crawler](https://github.com/iresil/creepyCrawler) at least once, and thus have created the `creepystore` database and filled its `stories` table. 
It does the following things:
- Mines `tokens`, `spans` and `sentiments` from each story and stores the results to the corresponding DB tables.
- Calculates and plots **coherence** scores, to determine the correct model configuration.
- Trains two models, one using the existing **category** data and one using each story's actual **text**.
- Makes **predictions** based on a list of input texts (ideally, this should not be included in the training set).

The main goal of this project is to group and categorize CreepyPasta stories in an automatic way.

## Plugin dependencies
- [**spacy 3.6.1**](https://pypi.org/project/spacy/)
- [**mysql 0.0.3**](https://pypi.org/project/mysql/)
- [**mysql-connector-python 8.1.0**](https://pypi.org/project/mysql-connector-python/)
- [**gensim 4.3.1**](https://pypi.org/project/gensim/)
- [**spacytextblob 4.0.0**](https://pypi.org/project/spacytextblob/)
- [**pyenchant 3.2.2**](https://pypi.org/project/pyenchant/)
- [**matplotlib 3.7.2**](https://pypi.org/project/matplotlib/)
- a locally installed [**MySQL**](https://dev.mysql.com/downloads/installer/) server instance, with a database called `creepystore` and the `stories` table already filled.

Any one of the already trained [spacy models](https://spacy.io/models/en) should also be installed, using the following command with the correct model name:
```
python -m spacy download en_core_web_md
```

## Text Mining
The `TextProcessor` class acts as an entry point for this process, but the actual tokenization (together with sentiment extraction, for optimization purposes) is done in `Tokenizer`.

It is called from `main.py`, using:
```
TextProcessor.mine_text(story_data)
```
Before it gets called, `StoryReader.get_stories()` must also be invoked, in order to return base story data to be processed.

You can keep `MINE_TEXT = False` in `definitions.py`, if you've already run this and you have its results stored in the database.

## Coherence Plotting
This process is managed by the `CoherenceCalculator` class, and it is performed separately for categories and separately for the actual texts of the stories.

It is called from `main.py`, using either the following for categories:
```
CoherenceCalculator.calculate_cat(story_items)
```
or the following for the actual story texts:
```
CoherenceCalculator.calculate_txt(story_items)
```

You can enable either process by setting `CATEGORY_COHERENCE = True` and `STORY_COHERENCE = True` in `definitions.py`. 

## Model training and Predictions
Both processes are managed by the `Classifier` class.

Both of them are initiated in `main.py`, **training** by calling:
```
classifier.train_models()
```
and **predictions** by calling:
```
classifier.make_predictions()
```
After training, models are stored in the `resources` folder and are loaded from there when predictions are requested.

You can enable model training by setting `TRAIN_MODELS = True`, and you can test that the predictions code is working (albeit using the training set) by setting `TEST_PREDICTIONS = True` in `definitions.py`.
