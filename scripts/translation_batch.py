"""Build a translation-first batch without mixing editorial review work."""
from scripts.editorial_queue import plan


def prepare_batch(inventory, edition, limit=25):
    if limit < 1:
        raise ValueError("limit must be positive")

    source_units = inventory.get("units", [])
    source_by_page = {unit["page"]: unit for unit in source_units}
    if len(source_by_page) != len(source_units):
        raise ValueError("Duplicate page in source inventory")

    edition_units = edition.get("units", [])
    target_pages = [unit.get("page") for unit in edition_units]
    if len(set(target_pages)) != len(target_pages):
        raise ValueError("Duplicate page in translation edition")
    unknown = set(target_pages) - set(source_by_page)
    if unknown:
        raise ValueError(f"Translation pages absent from source inventory: {sorted(unknown)}")

    tasks = plan(inventory, edition)
    translation_tasks = [task for task in tasks if task["agent"] == "translation"]
    review_tasks = [task for task in tasks if task["agent"] != "translation"]
    selected = translation_tasks[:limit]
    selected_pages = {task["page"] for task in selected}

    return {
        "source_sha256": inventory["source_sha256"],
        "limit": limit,
        "translation_tasks": selected,
        "translation_units": [
            unit for unit in source_units if unit["page"] in selected_pages
        ],
        "translation_remaining": len(translation_tasks),
        "review_backlog": review_tasks[:limit],
        "review_remaining": len(review_tasks),
    }
