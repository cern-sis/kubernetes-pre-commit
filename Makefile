.PHONY: all update clean

SHELL = /bin/bash -O dotglob -c

config_files = .pre-commit-config.yaml .prettierrc.yml .prettierignore .pre-commit-hooks requirements.txt
hooks = pre-commit pre-merge-commit
venv = .venv


define repo
	wget -LO main https://codeload.github.com/cern-sis/kubernetes-pre-commit/zip/refs/heads/main
	unzip -ou main -x "kubernetes-pre-commit-main/README.md" "kubernetes-pre-commit-main/.gitignore"
	mv kubernetes-pre-commit-main/* .
	rm -rf kubernetes-pre-commit-main main
endef

define in_venv
	source $(venv)/bin/activate &&
endef

define requirements
	$(in_venv) pip install --upgrade pip
	$(in_venv) pip install -r requirements.txt
endef

all: .git/hooks/$(hooks)

update: clean all

clean:
	rm -rf $(config_files)
	rm -rf $(venv)
	rm -f $(addprefix .git/hooks/, $(hooks))

$(config_files):
	$(repo)
	git add $(config_files)

$(venv): $(config_files)
	python -m venv $(venv)
	$(requirements)

.git/hooks/$(hooks): $(venv)
	$(in_venv) pre-commit install -t $(@F)
