"""
    This subpackage contains input validation for all structures.
"""

from .alternatives_profiles_input_validation import *
from .ranking_input_validation import *
from .flow_input_validation import *
from .sorting_input_validation import *
from .weights_input_validation import *
from .preference_input_validation import *
from .clustering_input_validation import *
from .choice_input_validation import *

__all__ = alternatives_profiles_input_validation.__all__ + ranking_input_validation.__all__ + \
          flow_input_validation.__all__ + sorting_input_validation.__all__ + weights_input_validation.__all__ + \
          preference_input_validation.__all__ + clustering_input_validation.__all__ + choice_input_validation.__all__
