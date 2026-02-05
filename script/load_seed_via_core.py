import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

from app import core_client


def read_csvs_as_payload(folder: Path) -> dict:
    payload = {}
    for name in [
        "municipality",
        "school",
        "teacher",
        "student",
        "course",
        "class_group",
        "enrolment",
        "assignment",
        "submission",
    ]:
        path = folder / f"{name}.csv"
        if path.exists():
            payload[name] = path.read_text(encoding="utf-8")
    return payload


async def main() -> int:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "output"
    if not folder.exists():
        print("Folder not found:", os.fspath(folder))
        return 1

    payload = read_csvs_as_payload(folder)
    if not payload:
        print("No CSVs found in", os.fspath(folder))
        return 1

    correlation_id = str(uuid.uuid4())
    try:
        res = await core_client.post_seed({"csv": payload, "mode": "demo"}, correlation_id=correlation_id)
        print(json.dumps({"ok": True, "correlationId": correlation_id, "result": res}, ensure_ascii=False))
        return 0
    finally:
        await core_client.aclose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))


