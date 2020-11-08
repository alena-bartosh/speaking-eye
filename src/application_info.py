class ApplicationInfo:

    def __init__(self, title: str, wm_name_re: str, tab_re: str, is_distracting: bool) -> None:
        self.title = title
        self.wm_name_re = wm_name_re
        self.tab_re = tab_re
        self.is_distracting = is_distracting

    def __eq__(self, other: object) -> bool:
        """
        Overrides the default implementation
        to use the object values instead of identifiers for comparison
        """
        if not isinstance(other, ApplicationInfo):
            return False

        if self.title != other.title:
            return False

        if self.wm_name_re != other.wm_name_re:
            return False

        if self.tab_re != other.tab_re:
            return False

        return self.is_distracting == other.is_distracting
