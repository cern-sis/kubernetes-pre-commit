# Kubernetes manifest repositories configuration

This repository contains all the configuration files needed to manage the CERN SIS kubernetes manifests repositories.

## Bootstrap

When creating a new repository you can install all the needed tools running:

```bash
wget https://raw.githubusercontent.com/cern-sis/kubernetes-pre-commit/main/Makefile
make
```
## Updates

To update the configuration of an existing repository:

```bash
make update
```

## Uninstall

To remove the configurations:

```bash
make clean
```
