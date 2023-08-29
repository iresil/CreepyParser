import sys


class OutputFormatter:
    @staticmethod
    def print_progress(percentage, previous_percentage):
        """ Display a sort of progress bar using the # character. """
        if percentage > previous_percentage:
            sys.stdout.write('#')
            if percentage == 100:
                sys.stdout.write('#')
                sys.stdout.flush()
                print("")
