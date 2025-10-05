# Bootstrap Instructions for tofu-aicl

## Overview

This document explains how to use the automated bootstrap pipeline to create the necessary Azure DevOps service connections for this project.

## The Problem: Pipeline Authentication

The main `azure-pipelines.yml` needs to push Docker images to the Azure Container Registry (ACR). To do this, it requires a **Docker Registry** service connection named `tofu-aicl-acr-connection`. This connection does not exist by default in a new project.

## The Solution: Automated Bootstrap Pipeline

We have an automated pipeline, `azure-pipelines-bootstrap.yml`, that creates this connection for you. It does this by checking out the `ancera-iac` repository and running the standardized `create-acr-service-connection.sh` script.

### The Bootstrap Paradox

To create a service connection, the bootstrap pipeline itself needs permission to talk to Azure. This requires a one-time manual authorization of a high-level **Azure Resource Manager (ARM)** service connection.

### How to Run the Bootstrap (One-Time Setup)

1.  **Go to Azure DevOps**: Navigate to the `tofu-aicl` project.
2.  **Run the Bootstrap Pipeline**: Find `azure-pipelines-bootstrap.yml` and click "Run".
3.  **Authorize Resources**: The pipeline will pause and ask for permission to use the `service-connection-placeholder`. An administrator must approve this. This is a one-time action.
4.  **Completion**: Once approved, the pipeline will run the script and create the `tofu-aicl-acr-connection`.

### After Bootstrap

Once the `azure-pipelines-bootstrap.yml` has run successfully one time:
- The `tofu-aicl-acr-connection` will exist.
- The main `azure-pipelines.yml` will be able to run without errors.
- All future pipeline runs will be fully automated.

This approach ensures that while a single manual approval is needed for security, the creation of the project-specific resources is fully automated and script-driven, following Ancera's best practices.
