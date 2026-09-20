# Probing XLM-R Representations for Morphosyntactic Generalization to Held-Out Lemmata in English, Italian, and Polish

Code, frozen intermediate data and results for the thesis of the same title by Filip Janczak, Bocconi University, 2026. `main.ipynb` runs the whole experiment.

A frozen XLM-R base readout (layer 8, last subword) feeds an L2-regularized logistic probe that
predicts UPOS and nominal Number in three Universal Dependencies treebanks. For each language and
task, two training sets of equal size share one test set and differ only in whether they contain
occurrences of the test lemmata, so the gap between them measures what lexical overlap was worth,
and a control task assigning random labels to lemma types separates representation from
memorization. Removing the overlap costs 0.09 to 0.14 accuracy and 0.18 to 0.28 macro-F1 on UPOS
and at most 0.007 on Number; the gap is significant in all six language-task cells, and the
lemma-disjoint probes still reach macro-F1 of 0.62 to 0.68 against majority baselines near 0.02.
Every design choice was fixed in `config.json` before any data were read.

## Repository layout

| Path | Contents |
|---|---|
| `main.ipynb` | The experiment, in the eleven parts below |
| `download_ud.py` | Downloads the three treebanks and checks them against `data/ud/MANIFEST.json` |
| `config.json` | Every design choice, written before any data are read (Table C.1) |
| `requirements.txt`, `requirements.in` | The locked environment (81 packages at exact versions) and the 14 direct dependencies it is built from |
| `data/ud/MANIFEST.json` | UD release, treebank commits, file checksums and download date (Tables C.2.2, C.2.3) |
| `cache/` | Task inventories, per-target metadata and the extraction record, the frozen splits, control labels and probe predictions |
| `results/` | Tables and reports (CSV, JSON), the run manifest, and `figures/` (PNG, 300 dpi) |

The eleven parts: 1 environment and reproducibility (Appendix C), 2 model and readout, 3 data and
task inventories, 4 target alignment and representation extraction, 5 paired split construction and
feasibility gate, 6 standardization and probe training, 7 control task, selectivity and primary
evaluation, 8 fragmentation analysis and exhibits (Results; Appendices A, B, F), 9 figures and
artifact index (Appendix E, and Figures 3.1, 5.1 and 5.2), 10 robustness extensions (Appendix D),
11 additional statistics quoted in the body.

## Setup

```
python -m venv .venv
.venv\Scripts\activate            # on Linux or macOS: source .venv/bin/activate
pip install -r requirements.txt
python download_ud.py
```

Python 3.11 is required and the notebook stops on any other version; no GPU is needed, because the
model is only used for inference. The lock installs the CPU build of PyTorch and was made on
Windows, so on macOS, which has no `+cpu` build, change `torch==2.13.0+cpu` to `torch==2.13.0`.
`download_ud.py` fetches the nine CoNLL-U files (76 MB) from the treebank commits recorded in
`data/ud/MANIFEST.json`, saving each only if its SHA-256 matches.

## Running the notebook

Open `main.ipynb` with the `.venv` environment as its kernel, start from the repository root, and
run all cells in order. From a fresh clone this recomputes every table, figure and statistic from
the frozen splits, control labels and predictions in `cache/` and the Appendix D results in
`results/`, without extracting any representation or refitting any probe.

The representations themselves (7.8 GB) are not in the repository, so Part 4's check of the cached
vectors against a fresh forward pass is skipped until something needs them. Deleting
`cache/predictions/` refits the main and control probes and extracts layer 8 first (48 minutes,
2.6 GB); deleting `results/extension_mlp_probe.csv` and `results/extension_layer_sweep.csv` refits
Appendix D and also extracts layers 4 and 11 (another 5.2 GB, and the 36 fits took 4.3 hours).

A run rewrites `config.json`, `results/run_manifest.json` (with the time of the run and your own
environment's versions) and the other files in `results/`. The committed files are the ones the
thesis reports: `git diff` shows what a run changed, and `git restore` puts the committed versions
back. The thesis-figure cell in Part 9 and all of Part 11 also run on their own, after the first
three cells of Part 1; Part 11 additionally needs the two parsing cells it uses, from Parts 3 and 4.

## The frozen splits

`cache/splits/` holds the splits the thesis reports, and the notebook reuses them. They were drawn
while the loop over the held-out lemmata still followed Python's per-session set order; that loop is
now sorted, so a rebuild is reproducible but draws a different, equally valid split, with the same
held-out lemmata and block sizes and different occurrences in each block. `cache/splits/SPLITS.json`
records the SHA-256 of all twelve files there, and Part 5 verifies them and re-checks the split
against the current inventory, so a missing or altered file stops the run instead of redrawing.
Deleting `SPLITS.json` too is the deliberate way to rebuild from scratch.

## Where each table and figure comes from

Files are in `results/` unless another folder is given.

| Thesis | Source | Part |
|---|---|---|
| Table 2.1 | None: the UD tagset. Its category column is `class_type` in [per_class_f1.csv](results/per_class_f1.csv) | 8 |
| Figure 3.1 | [figures/fig3_1_split_construction.png](results/figures/fig3_1_split_construction.png) | 9 |
| Table 3.1 | [inventory_report.json](results/inventory_report.json) | 3 |
| Table 4.1 | [extraction_report.json](results/extraction_report.json) | 4 |
| Table 4.2 | [split_report.json](results/split_report.json) | 5 |
| Table 5.1 | [main_results.csv](results/main_results.csv) | 6, 7 |
| Table 5.2 | [gap_table.csv](results/gap_table.csv) | 7 |
| Figure 5.1 | [figures/fig5_1_per_class_f1_drop.png](results/figures/fig5_1_per_class_f1_drop.png) | 9 |
| Table 5.3 | [mcnemar_table.csv](results/mcnemar_table.csv) | 7 |
| Table 5.4 | [main_results.csv](results/main_results.csv) (control and selectivity columns) | 7 |
| Figure 5.2 | [figures/fig5_2_task_vs_control.png](results/figures/fig5_2_task_vs_control.png) | 9 |
| Table 5.5 | `z_n_subwords` rows of [error_analysis_coefficients.csv](results/error_analysis_coefficients.csv) and [error_analysis_pooled.csv](results/error_analysis_pooled.csv); error counts from [error_analysis_model_size.csv](results/error_analysis_model_size.csv) | 8, 11 |
| Tables A.1.1, A.1.2 | [per_class_f1.csv](results/per_class_f1.csv) | 8 |
| Table A.1.3 | [open_closed_gap.csv](results/open_closed_gap.csv) (`NUM_open` rows) and [per_class_f1_support_check.csv](results/per_class_f1_support_check.csv) | 8 |
| Table A.1.4 | [open_closed_gap.csv](results/open_closed_gap.csv) (`NUM_closed` rows) | 8 |
| Table A.2 | [inventory_report.json](results/inventory_report.json) | 3 |
| Tables B.1.1, B.1.2 | [error_analysis_coefficients.csv](results/error_analysis_coefficients.csv) | 8 |
| Table B.1.3 | [error_analysis_pooled.csv](results/error_analysis_pooled.csv) | 8 |
| Table B.2 | [error_analysis_vif.csv](results/error_analysis_vif.csv) | 8 |
| Table B.3.1 | [error_analysis_standardization.csv](results/error_analysis_standardization.csv) | 11 |
| Table B.3.2 | [error_analysis_model_size.csv](results/error_analysis_model_size.csv) | 11 |
| Table C.1 | [config.json](config.json) (repository root) | 1 |
| Tables C.2.1 to C.2.3 | [run_manifest.json](results/run_manifest.json) | 1 |
| Table D.1.1 | The D.1 cell's MLP settings: the width from `config.json`, the rest scikit-learn defaults | 10 |
| Table D.1.2 | [extension_mlp_probe.csv](results/extension_mlp_probe.csv) | 10 |
| Table D.1.3 | [extension_summary.csv](results/extension_summary.csv) | 10 |
| Table D.2 | [extension_layer_sweep.csv](results/extension_layer_sweep.csv) (layers 4 and 11) and [main_results.csv](results/main_results.csv) (layer 8) | 10, 7 |
| Figures E.1.1, E.1.2 | [figures/accuracy_A_vs_B.png](results/figures/accuracy_A_vs_B.png), [figures/macro_f1_A_vs_B.png](results/figures/macro_f1_A_vs_B.png) | 9 |
| Figures E.2.1, E.2.2 | [figures/gap_ci_accuracy.png](results/figures/gap_ci_accuracy.png), [figures/gap_ci_macro_f1.png](results/figures/gap_ci_macro_f1.png) | 9 |
| Figures E.3.1, E.3.2 | [figures/selectivity_accuracy.png](results/figures/selectivity_accuracy.png), [figures/selectivity_macro_f1.png](results/figures/selectivity_macro_f1.png) | 9 |
| Tables F.1.1, F.1.2 | [h_sensitivity_summary.csv](results/h_sensitivity_summary.csv) | 8 |
| Table F.1.3 | [h_sensitivity_leave_one_out.csv](results/h_sensitivity_leave_one_out.csv) | 8 |
| Tables F.2.1, F.2.2 | [form_overlap.csv](results/form_overlap.csv) | 8 |
| Other numbers quoted in the text | [text_statistics.csv](results/text_statistics.csv), one row per statistic and cell, tagged with the section that quotes it | 11 |

In file and column names, `A` and `B` are the lexically overlapping and lemma-disjoint conditions,
and `delta` columns hold differences between them (condition A minus condition B).

## Data and model

The treebanks are not in the repository; `download_ud.py` fetches them from Universal Dependencies
release 2.18: [UD English-EWT](https://github.com/UniversalDependencies/UD_English-EWT) under
CC BY-SA 4.0, [UD Italian-ISDT](https://github.com/UniversalDependencies/UD_Italian-ISDT) under
CC BY-NC-SA 3.0, and [UD Polish-PDB](https://github.com/UniversalDependencies/UD_Polish-PDB) under
CC BY-NC-SA 4.0. The caches in `cache/` and the results files that list word forms or lemmata are
derived from the treebanks and fall under those licenses, which for Italian and Polish exclude
commercial use. The model, [xlm-roberta-base](https://huggingface.co/FacebookAI/xlm-roberta-base),
is downloaded from the Hugging Face Hub at run time, not redistributed here.
