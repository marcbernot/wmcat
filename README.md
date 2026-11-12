# wmcat

`wmcat` is a small Python catalog of thermographic watermark recordings (music manuscripts and
prints from SLUB Dresden and Staatsbibliothek zu Berlin) published on
[Zenodo](https://zenodo.org/). The catalog is a pandas DataFrame you filter with `search()`;
individual recordings (MATLAB `.mat` frame stacks) are downloaded on demand and displayed with `show()`.

[![Try it in your browser](https://img.shields.io/badge/try%20it-in%20your%20browser-F37626?logo=jupyter)](https://OWNER.github.io/wmcat/lab/index.html?path=getting_started.ipynb)

## Local quickstart

```sh
git clone https://github.com/OWNER/wmcat && cd wmcat
pixi run lab            # opens notebooks/getting_started.ipynb
# or: pip install -e ".[local]"
```
