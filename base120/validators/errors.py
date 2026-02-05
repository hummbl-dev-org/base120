from typing import Any, Mapping, Sequence


def resolve_errors(fms: list[str], err_registry: Sequence[Mapping[str, Any]]) -> list[str]:
    # FM30 dominance: escalation suppresses all other errors
    if "FM30" in fms:
        return sorted(
            str(entry.get("id", ""))
            for entry in err_registry
            if "FM30" in entry.get("fm", [])
        )

    errs: list[str] = []
    for entry in err_registry:
        fm_list = entry.get("fm", [])
        if any(fm in fms for fm in fm_list):
            errs.append(str(entry.get("id", "")))
    seen = set()
    return [x for x in sorted(errs) if not (x in seen or seen.add(x))]
