#!/usr/bin/env python3
"""Apply the content-planner priority rubric to a versioned JSON artifact."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "1.0"
COMMERCIAL_SCORES = {0, 8, 15, 22, 30}
STRATEGIC_SCORES = {2, 5, 8, 10}
FUNNEL_SCORES = {"TOFU": 8, "MOFU": 16, "BOFU": 25}


class ScoringError(ValueError):
    """Raised when priority inputs do not satisfy the public rubric."""


def _number(value: Any, path: str, *, minimum: float = 0, maximum: float | None = None) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, str) and value.strip().upper() == "N/A":
        return None
    if isinstance(value, bool):
        raise ScoringError(f"{path} must be numeric or null")
    try:
        number = float(str(value).replace(",", ""))
    except (TypeError, ValueError) as exc:
        raise ScoringError(f"{path} must be numeric or null") from exc
    if not math.isfinite(number) or number < minimum:
        raise ScoringError(f"{path} must be a finite number >= {minimum}")
    if maximum is not None and number > maximum:
        raise ScoringError(f"{path} must be <= {maximum}")
    return number


def _discrete_score(value: Any, allowed: set[int], path: str) -> int:
    number = _number(value, path, maximum=100)
    if number is None or not number.is_integer() or int(number) not in allowed:
        choices = ", ".join(str(item) for item in sorted(allowed))
        raise ScoringError(f"{path} must be one of: {choices}")
    return int(number)


def _percentile_ranks(values: Sequence[float | None]) -> list[float | None]:
    """Return PERCENTRANK.INC-like ranks with average ranks for ties."""
    indexed = sorted((value, index) for index, value in enumerate(values) if value is not None)
    result: list[float | None] = [None] * len(values)
    count = len(indexed)
    if count == 0:
        return result
    start = 0
    while start < count:
        end = start + 1
        while end < count and indexed[end][0] == indexed[start][0]:
            end += 1
        average_rank = ((start + 1) + end) / 2
        percentile = 100.0 if count == 1 else (average_rank - 1) / (count - 1) * 100
        for _, original_index in indexed[start:end]:
            result[original_index] = percentile
        start = end
    return result


def _demand_metric_points(value: float | None, percentile: float | None) -> int | None:
    if value is None or percentile is None:
        return None
    if value == 0:
        return 0
    if percentile <= 25:
        return 2
    if percentile <= 50:
        return 5
    if percentile <= 75:
        return 8
    return 10


def _feasibility_points(kd: float | None, site_dr: float | None) -> int | None:
    if kd is None:
        return None
    if site_dr is None:
        for upper, points in ((10, 15), (20, 13), (30, 11), (40, 8), (50, 5), (70, 2), (100, 0)):
            if kd <= upper:
                return points
        raise ScoringError("KD must be between 0 and 100")
    gap = kd - site_dr
    for upper, points in ((-20, 15), (-10, 13), (0, 11), (10, 8), (20, 5), (30, 2)):
        if gap <= upper:
            return points
    return 0


def _site_dr(metadata: Mapping[str, Any]) -> float | None:
    direct = metadata.get("site_domain_rating")
    if direct is not None:
        return _number(direct, "metadata.site_domain_rating", maximum=100)
    ahrefs = metadata.get("ahrefs")
    if isinstance(ahrefs, Mapping) and ahrefs.get("site_domain_rating") is not None:
        return _number(ahrefs.get("site_domain_rating"), "metadata.ahrefs.site_domain_rating", maximum=100)
    return None


def score_artifact(data: Any) -> dict[str, Any]:
    if not isinstance(data, Mapping):
        raise ScoringError("JSON root must be an object")
    if str(data.get("schema_version", "")) != SCHEMA_VERSION:
        raise ScoringError(f"schema_version must be {SCHEMA_VERSION!r}")
    metadata = data.get("metadata")
    rows = data.get("content_plan")
    if not isinstance(metadata, Mapping):
        raise ScoringError("metadata must be an object")
    if not isinstance(rows, list) or not rows:
        raise ScoringError("content_plan must be a non-empty array")
    if any(not isinstance(row, Mapping) for row in rows):
        raise ScoringError("every content_plan row must be an object")

    result = copy.deepcopy(dict(data))
    scored_rows = result["content_plan"]
    volumes = [_number(row.get("volume"), f"content_plan[{i}].volume") for i, row in enumerate(rows)]
    traffic = [
        _number(row.get("traffic_potential"), f"content_plan[{i}].traffic_potential")
        for i, row in enumerate(rows)
    ]
    volume_percentiles = _percentile_ranks(volumes)
    traffic_percentiles = _percentile_ranks(traffic)
    site_dr = _site_dr(metadata)

    for index, row in enumerate(scored_rows):
        path = f"content_plan[{index}]"
        primary = row.get("primary_keyword")
        if not isinstance(primary, str) or not primary.strip():
            raise ScoringError(f"{path}.primary_keyword must be a non-empty string")
        funnel = str(row.get("funnel", "")).upper()
        if funnel not in FUNNEL_SCORES:
            raise ScoringError(f"{path}.funnel must be TOFU, MOFU, or BOFU")
        commercial = _discrete_score(
            row.get("commercial_relevance_score"), COMMERCIAL_SCORES, f"{path}.commercial_relevance_score"
        )
        if commercial == 0:
            raise ScoringError(f"{path} has zero commercial relevance and must be excluded from the plan")
        strategic = _discrete_score(
            row.get("strategic_value_score"), STRATEGIC_SCORES, f"{path}.strategic_value_score"
        )
        funnel_points = FUNNEL_SCORES[funnel]
        volume_points = _demand_metric_points(volumes[index], volume_percentiles[index])
        traffic_points = _demand_metric_points(traffic[index], traffic_percentiles[index])
        if volume_points is None and traffic_points is None:
            demand_points = None
        elif volume_points is None:
            demand_points = min(20, traffic_points * 2)  # type: ignore[operator]
        elif traffic_points is None:
            demand_points = min(20, volume_points * 2)
        else:
            demand_points = volume_points + traffic_points

        kd = _number(row.get("kd"), f"{path}.kd", maximum=100)
        feasibility_points = _feasibility_points(kd, site_dr)
        known_points = commercial + funnel_points + strategic
        known_max = 30 + 25 + 10
        if demand_points is not None:
            known_points += demand_points
            known_max += 20
        if feasibility_points is not None:
            known_points += feasibility_points
            known_max += 15
        provisional = demand_points is None or feasibility_points is None
        uncapped = round(known_points / known_max * 100) if provisional else known_points
        score = min(74, uncapped) if provisional else uncapped
        priority = "P1" if score >= 75 else "P2" if score >= 50 else "P3"

        row["priority_score"] = score
        row["priority"] = priority
        row["score_is_provisional"] = provisional
        row["score_breakdown"] = {
            "commercial_relevance": commercial,
            "funnel": funnel_points,
            "demand": demand_points,
            "feasibility": feasibility_points,
            "strategic_value": strategic,
            "known_points": known_points,
            "known_maximum": known_max,
            "uncapped_provisional_score": uncapped if provisional else None,
            "site_domain_rating": site_dr,
        }

    order = {"P1": 0, "P2": 1, "P3": 2}
    scored_rows.sort(
        key=lambda row: (
            order[row["priority"]],
            -float(row["priority_score"]),
            str(row.get("topic", "")).casefold(),
            -(_number(row.get("volume"), "content_plan.volume") or 0),
            str(row.get("primary_keyword", "")).casefold(),
        )
    )
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply the deterministic content-planner priority rubric.")
    parser.add_argument("--input", required=True, type=Path, help="unscored UTF-8 JSON artifact")
    parser.add_argument("--output", required=True, type=Path, help="destination scored JSON artifact")
    parser.add_argument("--overwrite", action="store_true", help="explicitly replace an existing output file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.output.exists() and not args.overwrite:
            raise ScoringError(f"refusing to overwrite existing output: {args.output}")
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = score_artifact(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except (OSError, json.JSONDecodeError, ScoringError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"status": "ok", "output": str(args.output.resolve()), "rows": len(result["content_plan"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
