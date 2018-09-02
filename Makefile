python := $(PWD)/venv/bin/python
sed := sed -i.bak

SOURCES=lib bluprints scripts

# Check that the virtual env is active and error if not.
check-venv:
ifndef VIRTUAL_ENV
	$(error Not in a virtual environment. Activate your venv and try again)
endif

# Runs the code quality / linting tools across all applications.
lint: check-venv
	@scripts/lint

# Create a virtual environment using virtualenv.
venv:
	python3 -m venv venv
	@echo 'export PYTHONPATH=$(PWD)/lib:$$PYTHONPATH' >> venv/bin/activate
	@echo 'export PYTHONPATH=$(PWD)/blueprints:$$PYTHONPATH' >> venv/bin/activate
	$(sed) '/^VIRTUAL_ENV=/ a VIRTUAL_ENV_NAME="shopping_cart"' venv/bin/activate
	$(sed) 's/`basename \\"$$VIRTUAL_ENV\\"`/$$VIRTUAL_ENV_NAME/' venv/bin/activate

# Install all the dependencies.
install-dependencies: check-venv
	pip install pip --upgrade
	pip install -r requirements.txt

# Testing targets
init_test :
	@echo ""
	@echo "Running tests..."
	@echo "================"

test_integration : | init_test _test_integration
_test_integration :  # Allows this target to be run without it's dependencies.
	py.test ${ARGS} tests/integration

test_unit : | init_test _test_unit
_test_unit :  # Allows this target to be run without it's dependencies.
	py.test ${ARGS} tests/unit

test : | init_test _test
_test :  # Allows this target to be run without it's dependencies.
	py.test ${ARGS} tests

# Start the docker containers.
start-docker:
	docker-compose up -d


# Stop the docker containers.
stop-docker:
	docker-compose down

# Documentation
build-docs:
	sphinx-apidoc -o docs/api . tests
	sphinx-build docs/ site/
