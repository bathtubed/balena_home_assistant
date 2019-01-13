# Commands
DOCKER_TEMPLATE_COMPILER=dockerfile-template
DOCKERFILE_TEMPLATE=Dockerfile.template

# Device used for local testing
BALENA_MACHINE_NAME=pi
APP_NAME=blinds_with_home_assistant
BALENA_CMD=sudo balena

# Device name of the target
PI_ADDRESS=192.168.30.12
DEV_ID=165eaef5b57e6a80b5649dab1b929f7c

LOCAL_VARIABLE_OVERRIDE=

%/Dockerfile: %/$(DOCKERFILE_TEMPLATE)
	$(DOCKER_TEMPLATE_COMPILER) -f $< -d BALENA_MACHINE_NAME=$(BALENA_MACHINE_NAME) > $@

local-test: blinds/Dockerfile hass/Dockerfile git/Dockerfile
	$(BALENA_CMD) push $(PI_ADDRESS)

deploy: blinds/Dockerfile hass/Dockerfile git/Dockerfile
	$(BALENA_CMD) push $(APP_NAME)

clean:
	rm */Dockerfile
