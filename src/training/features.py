def _require(df, *cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns for feature extract: {missing}")


def _total_rooms(df, eps):
    _require(df, "bedrooms", "bathrooms")
    return df["bedrooms"] + df["bathrooms"]


def _bath_bed_ratio(df, eps):
    _require(df, "bedrooms", "bathrooms")
    return df["bathrooms"] / (df["bedrooms"].abs() + eps)


def _area_per_floor(df, eps):
    _require(df, "area", "floors")
    return df["area"] / (df["floors"].abs() + eps)


def _area_per_room(df, eps):
    _require(df, "area", "bedrooms", "bathrooms")
    rooms = df["bedrooms"] + df["bathrooms"]
    return df["area"] / (rooms.abs() + eps)


def _age_squared(df, eps):
    _require(df, "age")
    return df["age"] ** 2


_EXTRACT_FNS = {
    "total_rooms": _total_rooms,
    "bath_bed_ratio": _bath_bed_ratio,
    "area_per_floor": _area_per_floor,
    "area_per_room": _area_per_room,
    "age_squared": _age_squared,
}


def extract_features(df, config):
    fe = config.get("feature_engineering") or {}
    enabled = bool(fe.get("enabled", False))
    names = list(fe.get("extract") or [])
    eps = float(fe.get("eps", 1e-6))
    out = df.copy()
    extracted = []
    if not enabled:
        return out, extracted
    unknown = [n for n in names if n not in _EXTRACT_FNS]
    if unknown:
        raise ValueError(f"Unknown extractors: {unknown}. Available: {list(_EXTRACT_FNS)}")
    for name in names:
        out[name] = _EXTRACT_FNS[name](out, eps)
        extracted.append(name)
    return out, extracted
