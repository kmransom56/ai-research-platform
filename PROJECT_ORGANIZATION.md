# Chat Copilot Project Organization

This document describes the organized file structure for the Chat Copilot AI Research Platform.

## Directory Structure

### `/python/` - Python Scripts and Applications
Organized Python scripts for various platform functions.

#### `python/config-management/`
Configuration management and validation tools:
- `port-config-validator.py` - Port configuration validation and standardization
- `config_cleanup_utility.py` - FortiGate/device config backup cleanup
- `magentic_one_config.py` - Magentic-One system configuration
- `autogen_config.py` - AutoGen Studio configuration

#### `python/startup-scripts/`
Service startup and management scripts:
- `auto_startup_manager.py` - Systemd service creation and management
- `fix_startup_services.py` - Service diagnosis and fixing
- `startup_platform.py` - Main platform orchestrator with Power Automate integration

#### `python/services/`
Core AI service implementations:
- `magentic_one_server.py` - FastAPI web server for Magentic-One
- `magentic_one_implementation.py` - Full Magentic-One platform with AutoGen

#### `python/utilities/`
Utility scripts and tools:
- `vscode_web_integration.py` - VS Code Web integration
- `check-certificates.py` - SSL/TLS certificate monitoring
- `fix_startup_platform.py` - Platform maintenance utility
- `tailscale_certificates.py` - Tailscale HTTPS automation
- `power_automate_setup.py` - Power Automate integration
- `debug_config.py` - Configuration debugging

#### `python/examples/`
Example scripts and demonstrations:
- `magentic_one_simple.py` - Simplified Magentic-One implementation
- `autogen_examples.py` - AutoGen Studio workflow examples
- `main.py` - Basic Python template

### `/scripts/` - Shell Scripts
Organized shell scripts for platform management.

#### `scripts/platform-management/`
Core platform control scripts:
- `startup-platform.sh` - Primary startup script (v3.1)
- `startup-platform-clean.sh` - Alternative startup script (v3.0)
- `stop-platform.sh` - Platform shutdown
- `manage-platform.sh` - User-friendly interface
- `check-platform-status.sh` - Status checking
- `shutdown-platform.sh` - Graceful shutdown
- `startup-wrapper.sh` - Environment-based startup
- `install-ai-platform.sh` - Complete installation
- `start-ai-platform.sh` - Simple startup wrapper

#### `scripts/config-management/`
Configuration management and drift prevention:
- `validate-config.sh` / `config-validation.sh` - Config validation
- `protect-config.sh` - Configuration protection system
- `fix-configuration-drift.sh` - Comprehensive drift fix
- `monitor-config-changes.sh` - Change monitoring
- `config-monitor.sh` - Real-time monitoring
- `file-monitor.sh` - File-level monitoring
- `fix-all-ports.sh` - Port standardization
- `verify-restart-ports.sh` - Restart verification

#### `scripts/backup-recovery/`
Backup and recovery systems:
- `backup-configs.sh` - Manual configuration backup
- `backup-configs-auto.sh` - Automated backup (cron)
- `restore-config.sh` - Configuration restore
- `emergency-reset.sh` - Emergency recovery

#### `scripts/monitoring/`
System monitoring and health checks:
- `health-monitor.sh` - Continuous health monitoring

#### `scripts/deployment/`
Deployment and CI/CD scripts:
- `deploy.sh` - Deployment automation
- `create-deployment-package.sh` - Package creation

#### `scripts/infrastructure/`
Infrastructure setup and maintenance:
- `setup-tailscale.sh` - Tailscale setup
- `tailscale_https.sh` - HTTPS configuration
- `renew-certificates.sh` - Certificate renewal

#### `scripts/maintenance/`
System maintenance and cleanup:
- `system_cleanup.sh` - System package cleanup
- `cleanup-scripts.sh` - Script consolidation

#### `scripts/utilities/`
Utility and helper scripts:
- `switch-ai-provider.sh` - AI provider switching
- `add-github-collaborator.sh` - GitHub collaboration
- `quick-add-collaborator.sh` - Quick collaborator addition

### `/docs/` - Documentation
Organized documentation and guides.

#### `docs/project-meta/`
Project metadata and standard files:
- `README.md` - Main project documentation
- `CODE_OF_CONDUCT.md` - Microsoft code of conduct
- `CONTRIBUTING.md` - Contribution guidelines
- `SECURITY.md` - Security policy
- `SUPPORT.md` - Support policy
- `COMMUNITY.md` - Community guidelines

#### `docs/setup-guides/`
Installation and setup guides:
- `INSTALLATION_GUIDE.md` - Complete installation instructions
- `AUTOGEN_STUDIO_SETUP.md` - Multi-agent platform setup
- `MAGENTIC_ONE_SETUP.md` - Multi-agent orchestration setup
- `VSCODE_WEB_SETUP.md` - Browser development environment
- `WEBHOOK_SETUP.md` - GitHub webhook automation
- `GPU_OPTIMIZATION_72GB.md` - High-memory GPU optimization

#### `docs/documentation/`
Operational documentation:
- `USER_GUIDE.md` - End-user operation guide
- `SCRIPT_REFERENCE.md` - Script reference documentation
- `APPLICATIONS_DIRECTORY.md` - Service catalog and URLs
- `COMPLETE_AI_SERVICES_SUMMARY.md` - Service inventory

#### `docs/troubleshooting/`
Troubleshooting and problem resolution:
- `CONFIGURATION_DRIFT_SOLUTION.md` - Configuration stability solution
- `PORT_CONFIGURATION_SUMMARY.md` - Port standardization guide
- `RESTART_VERIFICATION_SUMMARY.md` - Restart mechanism verification
- `config-protection.md` - Technical protection summary
- `CLAUDE.md` - Configuration notes and troubleshooting

#### `docs/configuration-docs/`
Configuration-specific documentation:
- `AZURE_BACKUP_CONFIG.md` - Azure OpenAI backup configuration

#### `docs/business-docs/`
Business and commercialization documentation:
- `BUSINESS_PARTNERSHIP_GUIDE.md` - Business development guide

## Key Entry Points

### Primary Scripts
- `scripts/platform-management/startup-platform.sh` - Main startup (use this)
- `scripts/platform-management/manage-platform.sh` - User-friendly interface
- `python/startup-scripts/startup_platform.py` - Advanced orchestrator

### Primary Documentation
- `docs/project-meta/README.md` - Start here for overview
- `docs/setup-guides/INSTALLATION_GUIDE.md` - Installation instructions
- `docs/documentation/USER_GUIDE.md` - Day-to-day operations
- `docs/documentation/SCRIPT_REFERENCE.md` - Script reference

### Configuration Management
- `python/config-management/port-config-validator.py` - Port validation
- `scripts/config-management/fix-configuration-drift.sh` - Drift resolution
- `scripts/backup-recovery/backup-configs.sh` - Configuration backup

## Benefits of This Organization

1. **Clear Separation**: Scripts, Python code, and documentation are clearly separated
2. **Functional Grouping**: Files are grouped by their primary function
3. **Easy Navigation**: Related files are co-located
4. **Maintainability**: Easier to find and update related functionality
5. **Onboarding**: New developers can quickly understand the structure
6. **Scalability**: New files can be easily categorized and placed

## Migration Notes

All files have been moved to their appropriate directories based on their primary function and purpose. The organization maintains all existing functionality while providing a cleaner, more maintainable structure.

**Important**: Any scripts that reference moved files will need their paths updated. See the update log for details of changes made.