# Unsupervised Deep Generative Models for Anomaly Detection in Neuroimaging

This repository supports the review paper **"Unsupervised Deep Generative Models for Anomaly Detection in Neuroimaging"**. It provides materials and scripts to facilitate reproducibility and further exploration of the reviewed literature.

## Repository Contents

- **ArXiv Collector Script**
  - Script adapted from [`@koenraijer/arxivcollector`](https://github.com/koenraijer/arxivcollector) to recover ArXiv API queries used for literature search in the review.
  - Allows for transparent retrieval and updating of paper collections.

- **Included Papers**
  - All referenced papers are provided in BibTeX format (`ScreeningResults.bib`) for easy citation and reference management.

- **Summary Table**
  - The comprehensive table summarizing all included papers is available in CSV format (`Table2.csv`).
  - This table contains key attributes, methods, and findings, as presented in the review.

- **Barplot Reproduction Script**
  - Script (`barplots.py`) to reproduce the barplots shown in the publication.
  - Uses the CSV summary table and outputs publication-ready figures.

## Getting Started

1. **Literature Collection**
   - Use the ArXiv collector script to fetch or update the list of relevant papers.

2. **Bibliography**
   - Import `references.bib` into your reference manager (e.g., Zotero, Mendeley, BibDesk).

3. **Summary Table**
   - Open or analyze `Table2.csv` for paper-by-paper details.

4. **Barplot Generation**
   - Run `barplots.py` after ensuring all dependencies are installed (see below) and `Table2.csv` is in same directory.
   - Example:
     ```bash
     python barplots.py
     ```

## Requirements

- Python 3.x
- [arxivcollector](https://github.com/koenraijer/arxivcollector) (for API queries)
- matplotlib, pandas (for plotting and table management)

## Citation

TODO

---

For questions, suggestions, or contributions, please open an issue.
