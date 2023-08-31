import sys


class OutputFormatter:
    """ Helper class that deals with output formatting. """

    @staticmethod
    def print_progress(percentage, previous_percentage):
        """ Display a sort of progress bar using the # character. """
        if percentage > previous_percentage:
            sys.stdout.write('#')
            if percentage == 100:
                sys.stdout.write('#')
                sys.stdout.flush()
                print("")
