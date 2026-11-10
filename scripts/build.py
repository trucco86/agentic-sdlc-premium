#!/usr/bin/env python3
"""Prepare a private preview from the explicitly versioned source; never publish."""
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "source/current.pdf"
manifest = json.loads((root / "editorial/source_manifest.json").read_text())
out = root / "build/agentic-sdlc-preview.pdf"
if not source.is_file():
    raise SystemExit("BLOQUEADO: PDF-base ausente. Consulte editorial/source_manifest.json e importe source/current.pdf.")
actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
if actual_hash != manifest["sha256"]:
    raise SystemExit("BLOQUEADO: SHA-256 do PDF-base difere do manifesto. Atualize somente apos revisao editorial.")
out.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, out)
print(f"Previa privada validada: {out}")
