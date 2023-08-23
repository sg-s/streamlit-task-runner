
PID := $(shell cat streamlit.pid)

.PHONY: test coverage-report jupyter

jupyter:
	@echo "Installing kernel <streamlit_task_runner> in jupyter"
	-yes | jupyter kernelspec uninstall streamlit_task_runner
	poetry run python -m ipykernel install --user --name streamlit_task_runner




test:
	poetry run coverage run -m pytest -sx --failed-first
	-rm coverage.svg
	poetry run coverage-badge -o coverage.svg

coverage-report: .coverage
	poetry run coverage html --omit="*/test*"
	open htmlcov/index.html


start-app: stop-app
	@echo "Starting streamlit app.."
	@bash start-app.sh

stop-app:
	@echo "Stopping streamlit app..."
	-kill $(PID)


restart-app: stop-app start-app
	@echo "Restarting app..."