.PHONY: install_backend install_frontend init backend frontend clean

install_backend:
	cd backend && pip install -r requirements.txt

install_frontend:
	cd frontend && npm install

init: install_backend install_frontend
	@echo "Both backend and frontend dependencies installed"

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name node_modules -exec rm -r {} +
	find . -type d -name dist -exec rm -r {} + 

backend_test:
	cd backend && pytest
