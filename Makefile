# Commands
DOCKER_TEMPLATE_COMPILER=dockerfile-template
DOCKERFILE_TEMPLATE=Dockerfile.template

# Device used for local testing
BALENA_MACHINE_NAME=raspberrypi3
APP_NAME=ward-pi
BALENA_CMD=sudo balena

# Device name of the target
PI_ADDRESS=192.168.30.10

LOCAL_VARIABLE_OVERRIDE=

%/Dockerfile: %/$(DOCKERFILE_TEMPLATE)
	$(DOCKER_TEMPLATE_COMPILER) -f $< -d BALENA_MACHINE_NAME=$(BALENA_MACHINE_NAME) > $@

local-test: blinds/Dockerfile hass/Dockerfile
	$(BALENA_CMD) push $(PI_ADDRESS) -n $(APP_NAME) $(LOCAL_VARIABLE_OVERRIDE)
