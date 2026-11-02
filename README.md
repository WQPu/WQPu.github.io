# Wenqiang Pu — Academic Website

Jekyll source for [wqpu.github.io](https://wqpu.github.io/).

## Edit content

- Homepage and research directions: `_pages/about.md`
- Web CV and awards: `_data/cv.yml`
- Activities and talks: `_data/activities.yml`
- Teaching links: `_data/teaching.yml`
- Publications: `_bibliography/papers.bib` and `_data/publication_annotations.json`
- Homepage paper selection and short descriptions: `_data/selected_publications.yml`
- Shared appearance: `_sass/_academic.scss`

Generate both publication indexes after editing bibliography or topic annotations:

```sh
python3 tools/generate_publications_data.py
python3 -m unittest discover -s tools -p test_generate_publications_data.py -v
```

## Preview

Use Ruby from `.ruby-version` and the committed Bundler lockfile:

```sh
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

## Publish

Push reviewed source changes to `main`. GitHub Actions checks the publication
indexes, builds Jekyll, checks the public artifact, and deploys it with GitHub
Pages. Pages must use **GitHub Actions** as its publishing source. Check the
workflow result before treating a push as a successful website update.

```sh
python3 tools/check_publish_files.py
JEKYLL_ENV=production bundle exec jekyll build
python3 tools/check_publish_files.py --site _site
```

## Files that stay local

Private paper PDFs and evidence stay in `PubPaperPDFs/`. Recovery archives stay
in `.local-only/`. Both are Git-ignored and excluded from Jekyll. Local editor
settings, caches, and assistant instructions are not uploaded. PDF CV downloads
are disabled. Only the teaching PDFs explicitly linked in `_data/teaching.yml`
are allowed in the public source and artifact.

Keep generated `_site/` output out of source commits. The templates, Sass,
JavaScript, fonts, and vendored theme resources support the site build and UI.
