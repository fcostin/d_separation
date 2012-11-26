GREED := 1e-9

graph: proof_tree.svg

test:
	py.test --cov=. --cov-report=html .


proof_tree.dot:	main.py
	python $^ $(GREED)

proof_tree.svg:	proof_tree.dot
	unflatten -l 1 $^ | dot -Grankdir=LR -Tsvg -o $@

clean:
	rm -rf *.pyc
	rm -rf __pycache__
	rm -rf htmlcov
	rm -rf *.svg
	rm -rf *.dot

.PHONY: test graph clean
