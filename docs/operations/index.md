# Operations Hub

This hub organizes runtime and deployment documentation by operator workflow.

## Task-Based Navigation

1. Bootstrap host prerequisites
   - [System Bootstrap Script (`init_system.sh`)](../init_system.md)
2. Deploy or update a systemd instance
   - [Deployment Guide](../deployment.md)
   - [Quick Deploy](../deployment.md#quick-deploy)
3. Run services locally without systemd
   - [scripts/start_services.sh](../../scripts/start_services.sh)
   - [Runtime configuration](../guide.md#environment-variables)
4. Remove one deployed instance
   - [Uninstall One Instance](../deployment.md#uninstall-one-instance)

## Script Entry Points

- [scripts/init_system.sh](../../scripts/init_system.sh)
- [scripts/deploy.sh](../../scripts/deploy.sh)
- [scripts/start_services.sh](../../scripts/start_services.sh)
- [scripts/uninstall.sh](../../scripts/uninstall.sh)

## Documentation Ownership

- Canonical operational documentation is kept under `docs/`.
- `scripts/` contains executable code and only lightweight pointers.
