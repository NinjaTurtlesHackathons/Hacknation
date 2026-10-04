#!/usr/bin/env python3
"""Verify frozen release contents. Manifest deliberately excludes itself."""
from pathlib import Path
import hashlib,json,importlib.util
ROOT=Path(__file__).resolve().parents[2]
helper=Path(__file__).resolve().parent/'trial_archives/bundle_trials.py'
spec=importlib.util.spec_from_file_location('trial_bundle_restore',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.restore()
manifest=json.loads((Path(__file__).resolve().parent/'ARCHIVE_SHA256.json').read_text())
for name,digest in manifest['files'].items():
 if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('Hash mismatch: '+name)
print('PASS: exact release file hashes',len(manifest['files']))
