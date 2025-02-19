def clamp_downwards(num: int, mult: int) -> int:
    """
    Clamps the provided number downwards towards the provided mult.
    """

    return (num // mult) * mult
