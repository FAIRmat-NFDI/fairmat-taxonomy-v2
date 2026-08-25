# FAIRmat Taxonomy V2

Welcome to the **FAIRmat Taxonomy V2** repository. This project provides an ontological framework for materials science metadata, featuring automated CI/CD synchronization and an interactive web-based graph visualizer hosted on GitHub Pages.

---

## Repository Structure

```text
FAIRMAT-TAXONOMY-V2/
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline & GitHub Pages deployment
├── py-utils/
│   └── ttl-modulizer.py     # Python utility for splitting/combining Turtle files
├── web-app/
│   └── index.html           # Interactive D3.js + N3.js ontology visualizer
├── main.ttl                 # Primary single-file RDF/OWL Turtle ontology
└── requirements.txt         # Python project dependencies