#!/usr/bin/env python3
"""Validate existing private preview. No fabricated PDF is generated."""
from pathlib import Path
import shutil
source=Path("source/current.pdf")
out=Path("build/agentic-sdlc-preview.pdf")
if not source.is_file():
    raise SystemExit("BLOQUEADO: source/current.pdf ausente. Adicione a versao base aprovada antes de executar a geracao.")
out.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,out)
print(f"Previa privada preparada: {out}")
