# Contributing

## Development

```bash
pip install -e ".[dev]"
pre-commit install
```

## Releasing

1. Update the version in `pyproject.toml`
2. Add a new section to `CHANGELOG.md` with the version and date
3. Commit: `git commit -am "Release vX.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push && git push --tags`
6. Create a GitHub release from the tag: `gh release create vX.Y.Z --notes "See CHANGELOG.md"`

The PyPI publish workflow runs automatically when a GitHub release is published.
