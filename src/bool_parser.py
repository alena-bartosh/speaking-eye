class BoolParser:
    """
    Parse string True/False to boolean.
    Raise exception otherwise
    """

    @staticmethod
    def parse(value: str) -> bool:
        if value == 'True':
            return True
        elif value == 'False':
            return False
        else:
            raise ValueError(f'Unexpected value [{value}]')
