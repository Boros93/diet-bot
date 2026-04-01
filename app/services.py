from app.storage import load_profiles, load_state, save_profiles, save_state


def get_active_profile_name() -> str:
    return load_state()["active_profile"]


def set_active_profile(name: str) -> None:
    state = load_state()
    state["active_profile"] = name
    save_state(state)


def get_profile(profile_name: str) -> dict | None:
    profiles = load_profiles()["profiles"]
    return profiles.get(profile_name)


def list_profiles() -> list[str]:
    return list(load_profiles()["profiles"].keys())


def find_group_and_item(profile: dict, item_name: str):
    for group_name, group in profile["groups"].items():
        items = group["items"]
        if item_name in items:
            return group_name, items[item_name]
    return None, None


def convert_quantity(profile: dict, from_item: str, eaten_qty: float, to_item: str):
    group1, source = find_group_and_item(profile, from_item)
    group2, target = find_group_and_item(profile, to_item)

    if not source:
        return None, f"Alimento sorgente non trovato: {from_item}"
    if not target:
        return None, f"Alimento destinazione non trovato: {to_item}"
    if group1 != group2:
        return None, "I due alimenti non appartengono allo stesso gruppo."

    result = (eaten_qty / source["qty"]) * target["qty"]
    return {
        "group": group1,
        "from_unit": source["unit"],
        "to_unit": target["unit"],
        "result": result
    }, None


def remaining_quantities(profile: dict, source_item_name: str, eaten_qty: float):
    group_name, source = find_group_and_item(profile, source_item_name)

    if not source:
        return None, f"Alimento non trovato: {source_item_name}"

    ratio_consumed = eaten_qty / source["qty"]
    ratio_remaining = max(0.0, 1.0 - ratio_consumed)

    items = profile["groups"][group_name]["items"]
    remaining = {
        item_name: {
            "qty": item["qty"] * ratio_remaining,
            "unit": item["unit"]
        }
        for item_name, item in items.items()
    }

    return {
        "group": group_name,
        "ratio_consumed": ratio_consumed,
        "ratio_remaining": ratio_remaining,
        "remaining": remaining
    }, None


def upsert_table_item(profile_name: str, group_name: str, item_name: str, qty: float, unit: str):
    data = load_profiles()
    profiles = data.get("profiles", {})
    profile = profiles.get(profile_name)
    if not profile:
        return None, f"Profilo non trovato: {profile_name}"

    groups = profile.setdefault("groups", {})
    group = groups.setdefault(group_name, {"items": {}})
    items = group.setdefault("items", {})

    created = item_name not in items
    items[item_name] = {"qty": qty, "unit": unit}

    save_profiles(data)
    return {"created": created}, None


def delete_item_from_profile(profile_name: str, item_name: str):
    data = load_profiles()
    profiles = data.get("profiles", {})
    profile = profiles.get(profile_name)
    if not profile:
        return None, f"Profilo non trovato: {profile_name}"

    groups = profile.get("groups", {})
    for group_name, group in list(groups.items()):
        items = group.get("items", {})
        if item_name in items:
            del items[item_name]
            if not items:
                del groups[group_name]
            save_profiles(data)
            return {"group": group_name}, None

    return None, f"Alimento non trovato: {item_name}"


def add_group_to_profile(profile_name: str, group_name: str):
    data = load_profiles()
    profiles = data.get("profiles", {})
    profile = profiles.get(profile_name)
    if not profile:
        return None, f"Profilo non trovato: {profile_name}"

    groups = profile.setdefault("groups", {})
    if group_name in groups:
        return None, f"Gruppo già esistente: {group_name}"

    groups[group_name] = {"items": {}}
    save_profiles(data)
    return {"group": group_name}, None


def delete_group_from_profile(profile_name: str, group_name: str):
    data = load_profiles()
    profiles = data.get("profiles", {})
    profile = profiles.get(profile_name)
    if not profile:
        return None, f"Profilo non trovato: {profile_name}"

    groups = profile.get("groups", {})
    if group_name not in groups:
        return None, f"Gruppo non trovato: {group_name}"

    del groups[group_name]
    save_profiles(data)
    return {"group": group_name}, None
