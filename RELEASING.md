# Releasing new versions of docklib

## Requirements

- Virtual environment: `[[ -d .venv ]] || virtualenv .venv`
- Local clone with dev environment: `.venv/bin/pip install -e ".[dev]"`
- TestPyPI and PyPI accounts with Trusted Publishers configured ([details](https://docs.pypi.org/trusted-publishers/))

## Release Process

1. **Switch to local dev branch**.

1. **Update version** in:
    - `docklib/__init__.py`
    - `pyproject.toml`

1. **Update changelog**:
    - Reflect all recent changes
    - Add version number and release date
    - Add `## Unreleased` section
    - Update diff links at bottom

1. **Merge to main** and switch to local main branch.

1. **Create and push tag**:

   ```bash
   git tag -a v2.1.1 -m "Release version 2.1.1"
   git push origin v2.1.1
   ```

1. **Monitor and approve publication**:
   - Automatically publishes to [TestPyPI](https://test.pypi.org/project/docklib/) for testing
   - GitHub Actions will wait for manual approval to publish to production PyPI
   - Go to [Actions](https://github.com/homebysix/docklib/actions) → "Release" workflow → click "Review deployments" → approve "production"

1. **Create GitHub release** (manual):
   - Go to [Releases](https://github.com/homebysix/docklib/releases) and click "Create a new release"
   - Select the tag (v2.1.1), add release title and description from changelog

## Manual Fallback

If GitHub Actions fail:

```bash
# Test and build
.venv/bin/python -m coverage run -m unittest discover -v tests/
.venv/bin/python -m pip install build twine
.venv/bin/python -m build

# Publish
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*  # Then production
```
