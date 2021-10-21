LINTER = flake8
API_DIR = API
DB_DIR = db
REQ_DIR = requirements

FORCE:

prod: tests github

github: FORCE
	- git commit -a
	git push origin master

tests: lint unit

unit: FORCE
	cd $(API_DIR); nosetests --with-coverage --cover-package=API$*

lint: FORCE
	$(LINTER) $(API_DIR)/*.py

dev_env: FORCE
	pip3 install -r $(REQ_DIR)/requirements-dev.txt

docs: FORCE
	cd $(API_DIR); make docs
