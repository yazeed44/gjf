rm -rf dist/ src/gjf.egg-info/ && python -m build \
&& python3 -m twine upload --repository $1 dist/*