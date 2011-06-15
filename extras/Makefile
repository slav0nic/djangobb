.PHONY: pep8 pyflakes clean

pep8 :
	pep8 --statistics --show-pep8 --filename=*.py --exclude='venv' ../djangobb

pyflakes :
	find ../djangobb -name '*.py' -not \( -path '*/venv/*'  \) -exec pyflakes {} \;

clean :
	find ../djangobb -type f -name '*.pyc' -delete
