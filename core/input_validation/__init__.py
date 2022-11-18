"""
    This subpackage contains input validation for all structures.
"""

from .alternatives_profiles_input_validation import *
from .ranking_input_validation import *

__all__ = alternatives_profiles_input_validation.__all__ + ranking_input_validation.__all__
