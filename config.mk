################################################################################
# config.mk
#   Author: CptSpaceToaster
#   Email:  CptSpaceToaster@gmail.com
################################################################################
# Package name
PACKAGE := coeasm

GIT_HOOKS := $(patsubst hooks/%,.git/hooks/%,$(wildcard hooks/*))
REQ := $(wildcard *ments.txt)
DOT_REQ := $(addprefix .,$(REQ))

VENV := venv
VERSION := 3.4

PYTHON := $(VENV)/bin/python$(VERSION)
PIP := $(VENV)/bin/pip$(VERSION)
PIP_URL := https://bootstrap.pypa.io/get-pip.py

SOURCES := $(shell find $(PACKAGE) -name "*.py" -type f -not -path "*/test/*")

# Harvest the binary used to run the application from a Heroku styled Procfile
WEB_BIN := $(shell awk '$$1 ~ /^web:/ {print $$2;exit}' Procfile 2> /dev/null)
WEB_CMD := $(shell awk '$$1 ~ /^web:/ {$$1="";print $$0;exit}' Procfile 2> /dev/null | cut -d\  -f2-)

################################################################################
define check-tool
$(or $(shell which $(1)),$(error $(1) not installed, or defined in system path))
endef

# check tool requirements
ROOT_PYTHON := $(call check-tool,python$(VERSION))
WGET := $(call check-tool,wget)
