################################################################################
# Project Makefile
#   Author: CptSpaceToaster
#   Email:  CptSpaceToaster@gmail.com
################################################################################
######### Fallen and can't get back up? #########
.PHONY: help
help:
	@echo "Quick reference for supported build targets."
	@echo "----------------------------------------------------"
	@echo "  help                          Display this message."
	@echo "----------------------------------------------------"
	@echo "  hooks                         Install some git-hooks to help ensure safe commits."
	@echo "  list-sources                  Print the tracked files that can cause builds to trigger."
	@echo "----------------------------------------------------"
	@printf "  %-30s" "$(VENV)"
	@echo "Initialize a local virtual environment"
	@printf "  %-30s" "$(PIP)"
	@echo "Install pip in the local virtual environment"
	@echo "  reqs                          Install project dependencies in the local virtual environment"
	@echo "  install                       Generate an egg from the build, and create an executable in the virtual environment."
	@echo "  register                      Register this PC with the Python Package Index (PyPI)."
	@echo "  upload                        Upload the project and executable to PyPI under the registered account."
	@echo "----------------------------------------------------"
	@echo "  test                          Run some tests!"
	@echo "----------------------------------------------------"
	@echo "  clean                         Clean some things!"
	@echo "  clean-all                     Clean everything!"
	@printf "  %-30s" "clean-$(VENV)"
	@echo "Clean the virtual environment, and start anew."
	@echo "  clean-hooks                   Clean and uninstall the git-hooks"
	@echo "  clean-pycache                 Clean up python's compiled bytecode objects in the package"

################################################################################
include config.mk

######### Virtual Environment #########
$(VENV) $(PYTHON):
	test -d $(VENV) || $(ROOT_PYTHON) -m venv --without-pip $(VENV)

######### Pip #########
$(PIP): $(PYTHON)
	$(WGET) $(PIP_URL) -O - | $(PYTHON)

# This creates a dotfile for the requirements, indicating that they were installed
.PHONY: reqs
reqs: $(DOT_REQ)
.%ments.txt: %ments.txt $(PIP)
	test -s $< && $(PIP) install -Ur $<
	touch $@

######### Git Hooks #########
.PHONY: hooks
hooks: $(GIT_HOOKS)

.git/hooks/%: hooks/%
	ln -s ../../$< $@

######### Tests #########
.PHONY: test
test: $(PYTHON) $(DOT_REQ)
	$(PYTHON) -m unittest discover -s $(PACKAGE)
	$(PYTHON) setup.py check --strict --restructuredtext

######### Release #########
.PHONY: list-sources
list-sources:
	@echo $(SOURCES)
	@echo $(REQ)

.PHONY: install
install: .install
.install: $(PYTHON) $(DOT_REQ) $(SOURCES) setup.py
	$(PYTHON) setup.py develop
	$(PYTHON) setup.py install
	touch .install
	@echo "Installed locally in "$(VENV)"/bin/"$(PACKAGE)
	@command -v "xclip" &> /dev/null; \
	if [[ $$? -eq 0 ]] ; then \
		echo "$(VENV)"/bin/"$(PACKAGE)" | xclip -selection c; \
	fi

.PHONY: register
register: .register
.register: $(PYTHON) $(DOT_REQ) $(SOURCES) setup.py
	$(PYTHON) setup.py register --strict
	touch .register

.PHONY: upload
upload: .upload
.upload: .register $(PYTHON) $(DOT_REQ) $(SOURCES) setup.py
	$(PYTHON) setup.py sdist upload
	$(PYTHON) setup.py bdist_wheel upload
	touch .upload

######### Cleaning supplies #########
.PHONY: clean
clean:
ifneq ("$(wildcard .build)","")
	$(PYTHON) setup.py clean
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info/
endif
	rm -rf .build
	rm -rf .install
	rm -rf .upload

.PHONY: clean-all
clean-all: clean clean-$(VENV) clean-hooks clean-pycache

.PHONY: clean-$(VENV)
clean-$(VENV):
	rm -rf $(VENV)
	rm -rf $(DOT_REQ)

.PHONY: clean-hooks
clean-hooks:
	rm -rf $(GIT_HOOKS)

.PHONY: clean-pycache
clean-pycache:
	find $(PACKAGE) -path "*/__pycache__/*" -type f -delete
	find $(PACKAGE) -path "*/__pycache__" -type d -delete
