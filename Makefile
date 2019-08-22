################################################################################
#
# pgsql-auth-helper
#
################################################################################

ifndef VERBOSE
.SILENT:
endif

RM			= rm -f
ECHO			= echo -e
TAG			= etags
PIP			= pip
PYTHON			= python3
SHELL			= /bin/bash
WHICH                   = /usr/bin/which
WATCH                   = /usr/bin/watch
TEST                    = /usr/bin/test
ZIP			= /usr/bin/zip

SRC			= function.py secrets.py psql.py
AWS			= aws

VENV 			?= .venv
VENV_ACTIVATE		=. $(VENV)/bin/activate
ALIAS_NAME		?= $(shell bash -c 'read -p "Alias name: " alias; echo $$alias')

STACK			:=lambda-function-pgsql-auth-helper
FUNCTION_NAME		:=pgsql-auth-helper

ifndef TEMPLATE_FILE
TEMPLATE_FILE		:=function-template.yml
endif

ifdef EXAMPLE_TESTING
TEMPLATE_FILE		:=example_template.yml
endif

ifndef EXAMPLE_PARAMS
EXAMPLE_PARAMS		:=example_params.json
endif

BUCKET_PREFIX		:=lambda-dev-$(AWS_DEFAULT_REGION)
ifndef BUCKET_NAME
BUCKET_NAME		:=$(BUCKET_PREFIX)-$(AWS_DEFAULT_REGION)
endif

export VIRTUAL_ENV 	:= $(abspath ${VENV})
export PATH 		:= ${VIRTUAL_ENV}/bin:${PATH}

all			: venv template package


${VENV}			:
			$(PYTHON) -m venv $@


venv-install		: requirements_dev.txt | ${VENV}
			$(PIP) install -U pip
			$(PIP) install --upgrade -r requirements_dev.txt

venv			:
			test -d ${VENV} || $(MAKE) venv-install
			$(VENV_ACTIVATE)
			$(WHICH) python


clean-template		:
			$(RM) $(FUNCTION_NAME).yml

clean			: clean-template
			$(RM) $(FUNCTION_NAME).zip


template		: clean-template package $(VENV_ACTIVATE)
			$(AWS) cloudformation package --s3-bucket $(BUCKET_NAME) \
			--template-file $(TEMPLATE_FILE) \
			--output-template-file $(FUNCTION_NAME).yml

package			: clean
			$(ZIP) -r9 $(FUNCTION_NAME).zip $(SRC)

upload			: package
			$(AWS) s3 cp $(FUNCTION_NAME).zip s3://$(BUCKET_NAME)/$(FUNCTION_NAME).zip


create			: template $(VENV_ACTIVATE)
			$(AWS) cloudformation create-stack --stack-name $(STACK) \
			--template-body file://$(FUNCTION_NAME).yml \
			--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM \
			--parameters file://$(EXAMPLE_PARAMS)

update			: template publish $(VENV_ACTIVATE)
			$(AWS) cloudformation update-stack --stack-name $(STACK) \
			--template-body file://$(FUNCTION_NAME).yml \
			--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM \
			--parameters file://$(EXAMPLE_PARAMS)

delete			: clean-template
			$(AWS) cloudformation delete-stack --stack-name $(STACK)

validate		: $(VENV_ACTIVATE)
			$(AWS) cloudformation validate-template \
			--template-body file://$(FUNCTION_NAME).yml

events			: $(VENV_ACTIVATE)
			$(AWS) cloudformation describe-stack-events \
			--stack-name $(STACK) \
			--region $(AWS_REGION)

test			:
			$(AWS) cloudformation create-stack --stack-name psql-test \
			--template-body file://pgsql-auth-helper.yml \
			--parameters file://$(EXAMPLE_PARAMS) \
			--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
			--on-failure DELETE

update-test			:
			$(AWS) cloudformation update-stack --stack-name psql-test \
			--template-body file://pgsql-auth-helper.yml \
			--parameters file://$(EXAMPLE_PARAMS) \
			--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND

watch			:
			$(WATCH) --interval 1 "bash -c 'make events | head -40'"

.PHONY			: all venv venv-install clean clean-template package publish test update-test
