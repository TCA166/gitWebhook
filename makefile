
package:
	python3 -m build

install:
	python3 -m pip install --upgrade .

test:
	python3 -m unittest discover -v

clean:
	rm -rf build dist gitAppWebhook.egg-info __pycache__ .pytest_cache gitWebhook/__pycache__ doc/build
