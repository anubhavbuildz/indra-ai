# Terraform templates

Place reviewed, version-controlled Terraform examples here. The API does not
load templates or execute arbitrary files from this directory in V1. Plans
are created in server-generated per-operation workspaces; `apply` and
`destroy` remain disabled. Terraform state, provider caches, and plan files
can contain sensitive data and must not be committed.
