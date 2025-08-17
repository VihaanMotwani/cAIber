# Network Infrastructure
AWS VPC us-east-1 (10.0.0.0/16) and ap-southeast-1 (10.1.0.0/16).
Security Groups: 80/443 via Cloudflare; 5432 DB only from app; 6379 Redis from app.
Kubernetes NodePorts 30000-32767; Istio mTLS strict. DNS via Route 53; Site-to-site VPN.
