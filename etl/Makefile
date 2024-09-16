# ----------------------------------
#          INSTALL & TEST
# ----------------------------------

install:
	@pip install -e . -q
	@mv -f ./flatfindr/logins-template.py ./flatfindr/logins.py
	@echo 'flatfindr successfully installed'

test:
	@coverage run -m pytest tests/*.py
	@coverage report -m --omit="${VIRTUAL_ENV}/lib/python*"
	@rm -f raw_data/test_db.json

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr flatfindr-*.dist-info
	@rm -fr flatfindr.egg-info

UNAME := $(shell uname)
logins:
	@read -p "What is your facebook id (email or phone number) ?  " ID \
	&& read -p "What is your facebook password ?  " PWD \
	&& if [ "$(UNAME)" = "Darwin" ]; then sed -i '' -e "s/<ID>/$${ID}/g" -e "s/<PWD>/$${PWD}/g" ./flatfindr/logins.py \
	; else sed -i -e "s/<ID>/$${ID}/g" -e "s/<PWD>/$${PWD}/g" ./flatfindr/logins.py; fi

token:
	@read -p "What is your bot Access Token ? " TOKEN \
	&& if [ "$(UNAME)" = "Darwin" ]; then sed -i '' -e "s/<TOKEN>/$${TOKEN}/g" ./flatfindr/logins.py \
	; else sed -i -e "s/<TOKEN>/$${TOKEN}/g" ./flatfindr/logins.py; fi

all: clean install test

count_lines:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./scripts -name '*-*' -exec  wc -l {} \; | sort -n| awk \
		        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./tests -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

# ----------------------------------
#      UPLOAD PACKAGE TO PYPI
# ----------------------------------
PYPI_USERNAME=<AUTHOR>
build:
	@python setup.py sdist bdist_wheel

pypi_test:
	@twine upload -r testpypi dist/* -u $(PYPI_USERNAME)

pypi:
	@twine upload dist/* -u $(PYPI_USERNAME)
