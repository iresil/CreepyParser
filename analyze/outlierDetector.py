import numpy
import matplotlib.pyplot as plt
from database.tokenReader import TokenReader


class OutlierDetector:
    """ Helper class for finding outliers. """

    @staticmethod
    def find_clustered_tokens():
        """
        Attempts to retrieve all tokens that seem like suitable candidates for selection during training and prediction.
        The main parameter for outlier detection is how often a token appears in the training documents.
        This mainly means removing outliers using IQR. In this case, the related boxplot's bottom whisker was also removed,
        because if a token is so rare it probably shouldn't be included in the identified categories.
        """

        token_dist = TokenReader.get_token_distribution()
        outliers = OutlierDetector.__iqr_with_top_whisker(token_dist.values())
        result = {k: v for k, v in token_dist.items() if v not in outliers}
        return list(result.keys())

    @staticmethod
    def __iqr_with_top_whisker(data):
        """ Calculates IQR and returns non-outliers that aren't included in the related boxplot's bottom whisker. """

        q1, q3 = numpy.percentile(sorted(data), [25, 75])

        iqr = q3 - q1
        upper_bound = q3 + (1.5 * iqr)

        outliers = [x for x in data if x <= q1 or x >= upper_bound]

        return outliers

    @staticmethod
    def __iqr(data):
        """ Calculates IQR to filter out outliers. """

        q1, q3 = numpy.percentile(sorted(data), [25, 75])

        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = [x for x in data if x <= lower_bound or x >= upper_bound]

        return outliers

    @staticmethod
    def __boxplot(data):
        """ Displays a boxplot from the input data. """

        fig = plt.figure(figsize=(10, 7))

        plt.boxplot(data)
        plt.show()
