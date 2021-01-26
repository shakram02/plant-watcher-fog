# # See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.148.1/containers/python-3/.devcontainer/base.Dockerfile

# # [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
# ARG VARIANT="3"
# FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# EXPOSE 8000

# # [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends vim mosquitto-clients

# WORKDIR /app
# CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
FROM python:3-buster


ARG UNAME=python
ARG UID=1000
ARG GID=1000

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends vim zsh mosquitto-clients \
    && useradd -ms /bin/zsh ${UNAME}

USER $UNAME
RUN echo $(pwd) \
    && zsh -c "$(curl https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)" --unattended \
    && git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions \
    && sed -i "s/plugins=(.*)/plugins=(git zsh-autosuggestions)/g" ~/.zshrc \
    && zsh ~/.zshrc

WORKDIR /home/${UNAME}/app
CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"