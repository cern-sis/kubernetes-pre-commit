.PHONY: all

SHELL = /bin/bash -O dotglob -c

files = Makefile requirements.txt .prettierrc.yml .prettierignore .pre-commit-config.yaml
hooks = pre-commit pre-merge-commit
venv = .venv
ref = main


define fetch
	rm -f $(strip $(1))
	wget https://raw.githubusercontent.com/cern-sis/kubernetes-pre-commit/$(ref)/$(strip $(1))
endef

define in_venv
	source $(venv)/bin/activate &&
endef

all: .git/hooks/$(hooks)

$(files):
	$(call fetch, $(@F))
	git add $(@F)

$(venv): $(files)
	python -m venv $(venv)
	$(in_venv) pip install --upgrade pip
	$(in_venv) pip install -r requirements.txt

.git/hooks/$(hooks): $(venv)
	$(in_venv) pre-commit install -t $(@F)
