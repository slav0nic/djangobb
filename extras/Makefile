.PHONY: pep8 pyflakes clean

pep8 :
	pep8 --statistics --show-pep8 --filename=*.py --exclude='venv' ../djangobb_forum

pyflakes :
	find ../djangobb_forum -name '*.py' -not \( -path '*/venv/*'  \) -exec pyflakes {} \;

clean :
	find ../djangobb_forum -type f -name '*.pyc' -delete
