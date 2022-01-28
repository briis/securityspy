FROM ghcr.io/ludeeus/devcontainer/integration:stable

RUN apt update \
    && sudo apt install -y libpcap-dev ffmpeg vim curl jq libturbojpeg0 \
    && mkdir -p /opt \
    && cd /opt \
    && git clone --depth=1 -b dev https://github.com/home-assistant/core.git hass \
    && python3 -m pip --disable-pip-version-check install --upgrade ./hass \
    && python3 -m pip install pysecspy black isort pyupgrade pylint pylint_strict_informational \
    && ln -s /workspaces/securityspy/custom_components/securityspy /opt/hass/homeassistant/components/securityspy
