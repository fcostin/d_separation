test:
	py.test --cov=. --cov-report=html .

clean:
	rm -rf *.pyc
	rm -rf __pycache__
	rm -rf htmlcov
