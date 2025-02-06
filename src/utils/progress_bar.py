import numpy as np


class ProgressBar:
    @staticmethod
    def console_print(itr: float, max_value: float, info: str = '', start_str='\r'):
        percent = max(0.0, min(100.0, (itr / max_value * 100)))
        i_percent = 100.0 - percent
        print('{}{}{} {:5.1f}% {}'.format(start_str,
                                          "#" * int(np.ceil(percent)),
                                          "-" * int(np.ceil(i_percent)),
                                          percent,
                                          info), end=' ')

        if itr >= max_value:
            print('')
