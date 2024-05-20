FROM continuumio/miniconda3

# Set the working directory
WORKDIR /workspace

# Create a non-root user named vscode
RUN useradd -ms /bin/bash vscode

# Switch to the root user to install tree
USER root

# Install tree
RUN apt-get update && apt-get install -y tree

# Change to the vscode user
USER vscode

# Copy the environment.yml to the container
COPY environment.yml /workspace/

# Create the environment and clean up
RUN conda env create -f environment.yml \
    && conda clean -a

# Ensure the environment is activated when the container starts
RUN echo "source activate mlops_project_env" > ~/.bashrc

# Set the default command to bash
CMD ["/bin/bash"]