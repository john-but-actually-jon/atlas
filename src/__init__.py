""" The two lines below fix intra-module import issues when using pytest """

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent))
