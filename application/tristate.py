class Tristate:
    OnState = "On"
    OffState = "Off"
    UnknownState = " "

    @classmethod
    def to_list(cls) -> list[str]:
        """Returns a list with three states."""
        return [cls.UnknownState, cls.OffState, cls.OnState]

    @classmethod
    def to_toggle(cls) -> list[str]:
        """Returns a list with two states for toggle functionality."""
        return [cls.OffState, cls.OnState]
