"""Download UD treebanks (English-EWT, Italian-ISDT, Polish-PDB) at a pinned release and verify them.

data/ud/MANIFEST.json, which is part of the repository, records the release tag, each treebank's
commit at that tag and a sha256 per file; the notebook copies it into the run manifest (thesis
Appendix C.2). Every file is downloaded from its recorded commit and saved only if its sha256
matches, so the data are byte-identical to those the thesis used, and the manifest's "downloaded"
date is set to the day of the download. Without a manifest (e.g. after changing UD_RELEASE), a new
one is written from the commits the release tag points to.
"""
import hashlib
import json
from datetime import date
from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent / "data" / "ud"
MANIFEST = DATA_DIR / "MANIFEST.json"

UD_RELEASE = "r2.18"  # pinned stable UD release tag

TREEBANKS = {
    "UD_English-EWT": "en_ewt",
    "UD_Italian-ISDT": "it_isdt",
    "UD_Polish-PDB": "pl_pdb",
}
SPLITS = ["train", "dev", "test"]
RAW = "https://raw.githubusercontent.com/UniversalDependencies/{repo}/{commit}/{name}"
TAG_API = "https://api.github.com/repos/UniversalDependencies/{repo}/git/refs/tags/{tag}"


def tag_commit(repo: str) -> str:
    """Full commit sha the UD_RELEASE tag points to in `repo`."""
    r = requests.get(TAG_API.format(repo=repo, tag=UD_RELEASE), timeout=30)
    r.raise_for_status()
    obj = r.json()["object"]
    if obj["type"] == "tag":  # annotated tag -> dereference
        r = requests.get(obj["url"], timeout=30)
        r.raise_for_status()
        obj = r.json()["object"]
    return obj["sha"]


def download():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    recorded = MANIFEST.exists()
    manifest = (json.loads(MANIFEST.read_text(encoding="utf-8")) if recorded
                else {"ud_release": UD_RELEASE, "downloaded": None, "treebanks": {}})
    if manifest["ud_release"] != UD_RELEASE:
        raise SystemExit(f"{MANIFEST.name} records {manifest['ud_release']} but UD_RELEASE is "
                         f"{UD_RELEASE}; delete {MANIFEST.name} to record the new release")
    for repo, code in TREEBANKS.items():
        if not recorded:
            manifest["treebanks"][repo] = {"commit": tag_commit(repo), "files": {}}
        entry = manifest["treebanks"][repo]
        for split in SPLITS:
            dest = DATA_DIR / f"{code}-ud-{split}.conllu"
            r = requests.get(RAW.format(repo=repo, commit=entry["commit"], name=dest.name), timeout=120)
            r.raise_for_status()
            sha = hashlib.sha256(r.content).hexdigest()
            if recorded and sha != entry["files"][dest.name]:
                raise SystemExit(f"{dest.name}: sha256 {sha} does not match {MANIFEST.name} "
                                 f"({entry['files'][dest.name]}); the file was not saved")
            dest.write_bytes(r.content)
            entry["files"][dest.name] = sha
            print(f"  downloaded {dest.name} ({len(r.content)/1e6:.1f} MB)  sha256={sha[:12]}…"
                  + ("  matches" if recorded else ""))
    manifest["downloaded"] = date.today().isoformat()
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  {'updated' if recorded else 'wrote'} {MANIFEST.name} (downloaded {manifest['downloaded']})")


def verify():
    """Parse every file, check that each word has a form, lemma and UPOS, and print a short summary."""
    import conllu

    for repo, code in TREEBANKS.items():
        print(f"\n=== {repo} ===")
        for split in SPLITS:
            path = DATA_DIR / f"{code}-ud-{split}.conllu"
            with open(path, encoding="utf-8") as f:
                sents = conllu.parse(f.read())
            # real words only (skip multiword-token ranges and empty nodes)
            words = [t for s in sents for t in s if isinstance(t["id"], int)]
            with_number = [t for t in words if t["feats"] and "Number" in t["feats"]]
            missing = [f for f in ("form", "lemma", "upos") if any(t[f] is None for t in words)]
            status = "OK" if not missing else f"MISSING {missing}"
            print(f"  {split:5s}: {len(sents):6,} sents  {len(words):9,} words  "
                  f"Number on {len(with_number)/len(words):5.1%}  [{status}]")
        # sample: first 6 words of the first train sentence
        with open(DATA_DIR / f"{code}-ud-train.conllu", encoding="utf-8") as f:
            first = conllu.parse(f.read())[0]
        print(f"  sample: {first.metadata.get('text', '')[:60]}")
        for t in [t for t in first if isinstance(t["id"], int)][:6]:
            num = (t["feats"] or {}).get("Number", "—")
            print(f"    {t['form']:<12} lemma={t['lemma']:<12} upos={t['upos']:<6} Number={num}")


if __name__ == "__main__":
    print("Downloading...")
    download()
    print("\nVerifying...")
    verify()
