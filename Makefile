all:
	python Setup.py build_ext --inplace

test:	all
	python run_cheese.py

clean:
	@echo Cleaning 
	@rm -f bitset.c *.o *.so *~ core
	@rm -rf build
