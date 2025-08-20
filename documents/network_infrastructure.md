Acme Financial Services – Network Infrastructure (v3.2)

Overview:
Acme operates a hybrid infrastructure with 3 data centers (Singapore, Kuala Lumpur, Jakarta) 
and multi-cloud deployments across AWS (ap-southeast-1) and Azure (SEA region).

Core Components:
- Data Centers: SG1 (primary), MY1 (DR), ID1 (backup).
- Cloud: AWS ECS for container workloads; Azure AKS for orchestration.
- Databases: PostgreSQL 14 (HA cluster), MongoDB Atlas, Redis Enterprise.
- Networking: Cisco Firepower firewalls, Zscaler for remote access, Palo Alto VM-Series in cloud.
- Endpoints: 2,500 managed laptops (Windows 11 Enterprise), 600 servers (Linux Ubuntu 22.04).

Security Controls:
- Zero Trust: Okta for IAM, Duo MFA, conditional access policies.
- Segmentation: PCI-DSS compliant network zones (CDE separated from general workloads).
- Logging: FluentD + ElasticSearch pipeline; syslog forwarding from all firewalls.
- IDS/IPS: Suricata + Palo Alto Threat Prevention.
- EDR: CrowdStrike Falcon (enterprise license).

Third-Party SaaS Dependencies:
- GitHub Enterprise (code hosting)
- CircleCI (CI/CD)
- Atlassian Jira/Confluence
- Salesforce (CRM)
- ServiceNow (ITSM)

Known Weaknesses:
- Legacy VPN concentrator (Cisco ASA 9.x) still used by operations team.
- Flat network in MY1 data center (pending segmentation).
- Weak monitoring of container runtime security in Docker environments.
