def normalize_license_plate(
    plate: str | None,
) -> str | None:

    if not plate:
        return None

    return (
        plate
        .strip()
        .upper()
        .replace(" ", "")
    )