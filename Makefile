NAME = launcher
PREFIX = $(HOME)/.local/bin
VENV = .venv

build: dist/$(NAME)

dist/$(NAME): main.py | $(VENV)
	$(VENV)/bin/pyinstaller --onefile --name $(NAME) main.py

$(VENV):
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install pyinstaller

install: build
	install -Dm755 dist/$(NAME) $(PREFIX)/$(NAME)

uninstall:
	rm -f $(PREFIX)/$(NAME)

clean:
	rm -rf build dist $(NAME).spec $(VENV)

.PHONY: build install uninstall clean
