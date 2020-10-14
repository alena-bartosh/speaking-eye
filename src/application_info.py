class ApplicationInfo:

    def __init__(self, name: str, wm_name: str, tab: str, is_distracting: bool) -> None:
        self.name = name
        self.wm_name = wm_name
        self.tab = tab
        self.is_distracting = is_distracting

    def __eq__(self, other: 'ApplicationInfo') -> bool:
        """
        Overrides the default implementation
        to use the object values instead of identifiers for comparison
        """
        if not isinstance(other, ApplicationInfo):
            return False

        if self.name != other.name:
            return False

        if self.wm_name != other.wm_name:
            return False

        if self.tab != other.tab:
            return False

        return self.is_distracting == other.is_distracting
