
TESTS ?= \
   test_config.py \
   test_configErrors.py \
   test_create.py \
   test_createErrors.py \
   test_match.py \
   test_pull.py \
   test_pullIntoRepoDir.py \
   test_pullIntoVanillaDir.py \
   test_pullWithDeletedRsrcs.py \
   test_pullWithUnnormalizedPath.py \
   test_pullErrors.py \
   test_push.py \
   test_pushErrors.py \
   test_show.py \
   test_showErrors.py

MAKEFILE_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
include $(MAKEFILE_DIR)/Makefile.test

