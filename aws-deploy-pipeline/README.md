# AWS Deploy Pipeline

Starter template for deploying an app to AWS with Terraform + GitHub Actions.

## Contents
- `terraform/` infra skeleton
- `.github/workflows/deploy.yml` deployment pipeline template

## Notes

Before use, set repository secrets:
- `AWS_ROLE_TO_ASSUME`
- `AWS_REGION`