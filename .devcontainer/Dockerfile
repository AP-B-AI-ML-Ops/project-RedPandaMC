FROM continuumio/miniconda3

# Set the working directory
WORKDIR /workspace

# Copy the environment.yml to the container
COPY environment.yml /workspace/

# Create the environment and activate it
RUN conda env create -f environment.yml && conda clean -a

# Ensure the environment is activated when the container starts
CMD ["conda", "run", "--no-capture-output", "-n", "mlops_project_env", "/bin/bash"]