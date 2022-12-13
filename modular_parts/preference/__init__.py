from .M3_PrometheePreference import *
from .M4_PrometheeReinforcedPreference import *
from .M5_PrometheePreferenceWithInteractions import *
from .M6_PrometheeDiscordance import *
from .M7_PrometheeVeto import *

__all__ = M3_PrometheePreference.__all__ +\
          M4_PrometheeReinforcedPreference.__all__ + \
          M5_PrometheePreferenceWithInteractions.__all__ + \
          M6_PrometheeDiscordance.__all__ + M7_PrometheeVeto.__all__
