class ApplicationInfo:

    def __init__(self, name: str, wm_name: str, tab: str):
        self.name = name
        self.wm_name = wm_name
        self.tab = tab

    def __eq__(self, other):
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

        return self.tab == other.tab
