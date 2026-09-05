"""
Dataset Generator
Generates 10,000 realistic IT support tickets across 10 departments
"""
import os
import random
import pandas as pd
from datetime import datetime, timedelta, timezone

# ─── Department definitions ────────────────────────────────────────────────────
DEPARTMENTS = {
    "Hardware": {
        "keywords": ["laptop", "desktop", "keyboard", "mouse", "monitor", "printer", "battery",
                     "charger", "screen", "RAM", "hard drive", "SSD", "USB", "docking station",
                     "headset", "webcam", "power adapter", "projector", "speaker", "cable"],
        "templates": [
            "My {device} is not turning on. It was working fine yesterday but now completely unresponsive.",
            "The {device} screen is flickering and showing display artifacts. Tried restarting but no luck.",
            "Keyboard on my {device} has multiple keys not responding including {keys}.",
            "Battery on my {device} drains in less than 1 hour even when just browsing the web.",
            "The USB port on my {device} stopped working after I plugged in the {accessory}.",
            "My {device} overheats quickly and shuts down automatically during normal usage.",
            "The charging cable for my {device} is broken. Need a replacement urgently.",
            "Hard drive on workstation {device} is making clicking sounds. Worried about data loss.",
            "RAM upgrade needed for my {device}. Current 8GB is insufficient for development work.",
            "Monitor showing no signal when connected to {device} via HDMI cable.",
            "Printer in {location} is offline and not accepting print jobs from any computer.",
            "My mouse cursor jumps erratically across the screen without any input.",
            "Laptop hinge is broken on {device}. Screen almost falling off.",
            "New hardware device {accessory} not being recognized by the system.",
            "Speaker quality on my {device} has degraded significantly, producing distorted audio.",
            "Webcam not detected during video calls on {device}.",
            "Laptop touchpad completely unresponsive, external mouse works fine.",
            "Power button on my {device} needs to be pressed multiple times before it boots.",
            "Memory on device is showing 6GB instead of 8GB installed.",
            "External SSD {accessory} not mounting on any of the available ports.",
        ],
    },
    "Software": {
        "keywords": ["application", "software", "install", "update", "crash", "error", "license",
                     "Outlook", "Excel", "Word", "Teams", "browser", "Adobe", "antivirus",
                     "Windows", "macOS", "patch", "update", "version", "compatibility"],
        "templates": [
            "Microsoft Outlook crashes every time I try to open an email with an attachment.",
            "Unable to install {software} due to permission error: Access Denied 0x80070005.",
            "Excel file becomes unresponsive when working with large datasets over 50,000 rows.",
            "Adobe Acrobat shows license expired message but subscription was renewed last week.",
            "Windows update stuck at 45% for over 6 hours on {device}.",
            "{software} application shows runtime error .NET Framework missing when launched.",
            "Browser {software} keeps resetting default search engine to Bing after each restart.",
            "Teams application audio stops working mid-meeting. Had to rejoin 3 times.",
            "Cannot open {file_type} files. Associated application not installed or corrupted.",
            "Software {software} throwing SQL connection error on startup. Database config issue.",
            "License for {software} expired and team cannot access critical features.",
            "Antivirus flagging legitimate application {software} as threat and quarantining it.",
            "Application {software} requires admin privileges to run but we only have standard access.",
            "Zoom not connecting, getting error 1006 Network Connection Timeout.",
            "VSCode extensions not loading after recent system update.",
            "Slack notifications not appearing on desktop even with notifications enabled.",
            "Chrome browser memory usage exceeds 8GB causing system slowdown.",
            "Application crashes after OS upgrade to Windows 11 version 23H2.",
            "Cannot export reports from {software} - getting invalid format error.",
            "Two-factor authentication app not generating correct codes after phone reset.",
        ],
    },
    "Network": {
        "keywords": ["internet", "wifi", "VPN", "network", "connection", "bandwidth", "firewall",
                     "DNS", "IP", "router", "switch", "ethernet", "ping", "latency", "proxy",
                     "port", "NAT", "DHCP", "SSL", "certificate"],
        "templates": [
            "VPN connection fails with error 800 when trying to connect from home office.",
            "Internet connection dropping every 30 minutes on my workstation in {location}.",
            "Cannot access internal company network resources after connecting to VPN.",
            "WiFi speed extremely slow in {location}, only getting 2 Mbps instead of 100 Mbps.",
            "DNS resolution failing for external websites but internal resources work fine.",
            "Network printer in {location} unreachable from workstations but visible on network.",
            "Cannot connect to company SharePoint through browser, getting SSL certificate error.",
            "Remote desktop connection timing out when attempting to connect to server {server}.",
            "Network drive Z: disconnects automatically every few hours requiring manual reconnect.",
            "Firewall blocking access to required vendor website {url}. Need exception added.",
            "Ethernet port in conference room {location} not providing network connectivity.",
            "VPN throughput drops to under 1 Mbps making remote work impossible.",
            "IP conflict error on workstation. Multiple devices assigned same IP address.",
            "Cannot access {url} from office network but can access through mobile hotspot.",
            "Network bandwidth saturation in {location} during morning hours 9-11 AM.",
            "Proxy settings preventing access to cloud storage services.",
            "WiFi keeps disconnecting on {device} every 10 minutes.",
            "Unable to reach server {server} on port 443, connection refused.",
            "Network certificate expired for internal portal causing browser warnings.",
            "Packet loss over 30% causing voice and video call quality issues.",
        ],
    },
    "Database": {
        "keywords": ["database", "SQL", "MySQL", "Oracle", "PostgreSQL", "query", "connection",
                     "backup", "restore", "timeout", "deadlock", "index", "table", "schema",
                     "replication", "performance", "stored procedure", "transaction", "lock"],
        "templates": [
            "Database connection timeout error in production application. Cannot connect to {db}.",
            "SQL query taking over 10 minutes to execute on table with 5 million records.",
            "Database {db} replication is lagging by 4 hours. Primary and replica out of sync.",
            "Deadlock detected in {db} causing transaction failures in payment processing module.",
            "Database backup job failed at 2 AM. Backup file size is 0 bytes.",
            "Table {table} has grown to 500GB and is causing disk space alerts on server.",
            "Cannot connect to {db} database from application server after server maintenance.",
            "Stored procedure sp_GenerateReport failing with insufficient memory error.",
            "Database indexes need rebuild. Query performance degraded by 80% this week.",
            "MySQL server crashed and auto-restart failed. Manual intervention required.",
            "Cannot restore database from backup due to version incompatibility.",
            "Database user account locked after multiple failed login attempts.",
            "Report query crashing application with out of memory exception at runtime.",
            "Database schema migration failed during deployment. Rollback needed.",
            "Connection pool exhausted. All {db} connections in use during peak hours.",
            "Corrupt data found in {table} table after power failure during write operation.",
            "Database logs growing uncontrollably. Log file now 200GB on disk.",
            "Need database read replica for reporting queries to reduce load on primary.",
            "Foreign key constraint violation preventing record deletion in {table}.",
            "Database access for user {user} needs permission update to include SELECT on new tables.",
        ],
    },
    "Cloud": {
        "keywords": ["AWS", "Azure", "GCP", "cloud", "S3", "EC2", "storage", "bucket", "VM",
                     "instance", "container", "Kubernetes", "Docker", "deployment", "IAM",
                     "serverless", "Lambda", "scaling", "load balancer", "CDN"],
        "templates": [
            "AWS EC2 instance {instance} not starting after stop/start cycle in us-east-1.",
            "Azure blob storage container {container} access denied for service account.",
            "Cloud deployment pipeline failing at Docker build step with dependency error.",
            "Kubernetes pod {pod} keeps crashing with OOMKilled error. Need memory increase.",
            "S3 bucket {bucket} CORS policy blocking API requests from frontend application.",
            "GCP Cloud Function timing out after 60 seconds on large file processing.",
            "Azure VM disk IO extremely slow after recent migration to new storage tier.",
            "Load balancer health checks failing for {service} causing traffic disruption.",
            "CloudWatch alarm triggered for high CPU on {instance} above 95% for 30 minutes.",
            "Need to provision new cloud environment for {project} development team.",
            "Cloud storage costs exceeded budget by 40%. Need cost optimization analysis.",
            "IAM role {role} missing permissions to access required AWS services.",
            "Container image push to ECR failing with authentication token expired error.",
            "Auto-scaling group not scaling up during load test. Min instances stuck at 2.",
            "CDN caching stale content after deployment. Cache invalidation not working.",
            "Cloud database RDS instance {instance} storage almost full at 95%.",
            "Serverless function cold start latency too high causing timeout in chain.",
            "VPC peering connection between {vpc1} and {vpc2} routing not working correctly.",
            "SSL certificate for cloud domain expired. Urgent renewal needed.",
            "Terraform state file corruption preventing infrastructure changes.",
        ],
    },
    "Security": {
        "keywords": ["password", "login", "access", "permission", "breach", "phishing", "malware",
                     "antivirus", "firewall", "encryption", "certificate", "2FA", "MFA", "audit",
                     "vulnerability", "patch", "compliance", "data", "suspicious", "unauthorized"],
        "templates": [
            "Received suspicious phishing email from {sender} asking for credentials. Reporting.",
            "Account locked after multiple failed login attempts. Need immediate unlock.",
            "Possible malware infection on {device}. Unusual processes detected in Task Manager.",
            "Unauthorized access attempt detected from IP {ip} on admin portal.",
            "2FA authentication device lost. Need access restored through alternative method.",
            "Suspicious file attachment opened accidentally. Need security scan.",
            "User {user} account showing login activity from country {country} - suspicious.",
            "Security audit found unpatched vulnerability CVE-{cve} on production server.",
            "Data encryption certificate expiring in 7 days. Renewal process needed.",
            "Compliance check failing - user accounts with admin rights need review.",
            "Password policy change required. Current passwords expire after 90 days.",
            "Ransomware alert triggered on {device}. Files showing .locked extension.",
            "SSL certificate expired on {domain} causing browser security warnings.",
            "Need emergency revocation of access for terminated employee {user}.",
            "Security scan showing open port {port} that should be restricted.",
            "User granted incorrect permission level - has admin when should be read-only.",
            "Cannot enable MFA on account due to phone number change.",
            "Audit log shows bulk data export by {user} - needs investigation.",
            "Firewall rule change required to allow vendor IP {ip} access.",
            "Security incident: laptop {device} left unattended with unlocked screen.",
        ],
    },
    "HR": {
        "keywords": ["leave", "payroll", "employee", "onboarding", "offboarding", "benefits",
                     "policy", "training", "attendance", "performance", "HR", "salary", "contract",
                     "appraisal", "holiday", "PTO", "resignation", "hire", "handbook"],
        "templates": [
            "Unable to submit leave request in HR portal. Getting page not found error.",
            "Payslip for month of {month} not generated in employee self-service portal.",
            "New employee {name} joining on {date}. Need system access and equipment setup.",
            "Training certification for {course} not reflecting in employee profile.",
            "Attendance records showing incorrect data for week of {date}.",
            "Need to update emergency contact information in HR system.",
            "Benefits enrollment period ending. Unable to access benefits selection page.",
            "Performance review form not appearing in system for appraisal cycle.",
            "Cannot access PTO balance in HR portal. Shows 0 days even after accrual.",
            "Employee handbook policy needs update after new regulation change.",
            "Onboarding checklist items not marking as complete despite finishing them.",
            "Payroll tax deduction seems incorrect for last 2 months.",
            "Need HR clearance for internal transfer to {department} team.",
            "Company holiday calendar not updated in system for next fiscal year.",
            "Contract renewal documents not available in employee document portal.",
            "Resignation letter submission portal giving server error 500.",
            "Cannot enroll in health insurance plan before open enrollment deadline.",
            "Employee ID card needs replacement after loss. Initiate reissue process.",
            "Probation period completion not reflected in employee status.",
            "Training module for {course} compliance not loading in LMS system.",
        ],
    },
    "Finance": {
        "keywords": ["invoice", "payment", "expense", "budget", "accounting", "reimbursement",
                     "purchase order", "vendor", "billing", "tax", "audit", "financial",
                     "ERP", "SAP", "Oracle Financials", "reconciliation", "approval"],
        "templates": [
            "Expense claim submitted {date} not yet reimbursed. Amount {amount} pending approval.",
            "Cannot submit expense report. Portal showing validation error on receipt upload.",
            "Vendor invoice {inv_no} needs urgent approval to avoid late payment penalty.",
            "Purchase order for {item} not approved after 2 weeks of submission.",
            "Budget allocation for Q{quarter} project not yet transferred to department.",
            "ERP system not generating correct financial reports for month-end close.",
            "Tax filing module in financial system showing incorrect GST calculation.",
            "Cannot access payment approval workflow in SAP. Getting authorization error.",
            "Financial audit report for {period} has data discrepancy in accounts payable.",
            "Expense category {category} not available in expense management system.",
            "Credit card statement reconciliation failing due to duplicate transaction entry.",
            "Cost center code {code} not recognized in budget tracking system.",
            "Need emergency fund transfer approval for {project} operational expenses.",
            "Payroll integration with accounting system showing mismatch in GL entries.",
            "Cannot generate profit and loss statement for {period} due to system error.",
            "Vendor payment {amount} marked as paid but vendor not received. Investigation needed.",
            "Currency conversion rates not updated in financial system for this month.",
            "Budget overspend alert for department {dept}. Need approval for additional funds.",
            "Invoice approval chain broken after manager {name} departed company.",
            "Annual subscription renewal for {service} invoice not matching contract terms.",
        ],
    },
    "CRM Support": {
        "keywords": ["CRM", "Salesforce", "customer", "lead", "opportunity", "pipeline", "contact",
                     "account", "deal", "report", "dashboard", "integration", "sync", "workflow",
                     "automation", "email template", "record", "field", "user access"],
        "templates": [
            "Unable to login to Salesforce CRM. Getting invalid credentials error.",
            "CRM pipeline view not showing latest opportunities added this week.",
            "Customer contact records not syncing from email to CRM automatically.",
            "Salesforce workflow automation not triggering on lead status change.",
            "CRM dashboard charts showing incorrect data for current quarter.",
            "Cannot create new account in CRM. Required field {field} not appearing.",
            "Lead assignment rules not routing leads to correct sales representatives.",
            "Email template in CRM not rendering correctly when sending to customers.",
            "CRM mobile app not syncing data when switching between offline and online.",
            "Duplicate customer records need merging. Found {count} duplicates for {company}.",
            "Report {report} in CRM not showing data beyond {date}. Export incomplete.",
            "Integration between CRM and ERP broke after system update. Orders not syncing.",
            "CRM user {user} cannot access accounts from {region} due to permission issue.",
            "Custom field {field} added to CRM not appearing in email templates.",
            "Mass email campaign from CRM bouncing for {count} contacts. List cleanup needed.",
            "Opportunity stage not progressing automatically despite meeting criteria.",
            "CRM API calls failing with 429 Too Many Requests error from integration.",
            "Sales forecast in CRM showing inaccurate numbers due to closed deal weighting.",
            "Cannot deactivate CRM user account for departed employee {user}.",
            "Activity timeline in CRM account not showing recent call logs from team.",
        ],
    },
    "DevOps": {
        "keywords": ["CI/CD", "pipeline", "Jenkins", "GitHub", "deployment", "build", "Docker",
                     "Kubernetes", "monitoring", "logging", "Ansible", "Terraform", "server",
                     "infrastructure", "release", "rollback", "environment", "staging", "production"],
        "templates": [
            "CI/CD pipeline for {project} failing at unit test stage with {error} error.",
            "Jenkins build job stuck in queue for over 2 hours. Agents appear offline.",
            "Production deployment for release {version} failed. Need immediate rollback.",
            "Docker container for {service} exiting with code 137. OOM killer suspected.",
            "GitHub Actions workflow failing with secret not found error in CI.",
            "Kubernetes deployment {deploy} stuck in Pending state. No available nodes.",
            "Monitoring alerts for {service} not triggering despite CPU exceeding threshold.",
            "Log aggregation for {service} in ELK stack stopped. Missing recent logs.",
            "Ansible playbook for server {server} configuration failing at task {task}.",
            "Terraform plan showing unexpected destroy of production database resource.",
            "SSL certificate renewal automation failed for {domain}. Cert expires in 3 days.",
            "Staging environment for {project} out of sync with production configuration.",
            "Artifact storage disk full on Jenkins master. Build artifacts not being pruned.",
            "Need new environment provisioned for {project} load testing before release.",
            "Blue-green deployment switch failed. Traffic still routing to old version.",
            "Database migration script in deployment pipeline failing on {env} environment.",
            "Container registry pulling old image tag despite specifying latest version.",
            "Service mesh circuit breaker opening too aggressively for {service}.",
            "On-call alert fatigue. Need alert threshold tuning for {monitoring_tool}.",
            "Helm chart deployment of {chart} failing with values validation error.",
        ],
    },
}

PRIORITIES = ["low", "medium", "high", "critical"]
PRIORITY_WEIGHTS = [0.25, 0.40, 0.25, 0.10]

STATUSES = ["open", "in_progress", "resolved", "closed"]
STATUS_WEIGHTS = [0.35, 0.25, 0.30, 0.10]

LOCATIONS = ["Floor 1", "Floor 2", "Floor 3", "Building A", "Building B", "Conference Room A", "Conference Room B"]
DEVICES = ["laptop", "desktop", "workstation", "MacBook Pro", "Dell Latitude", "HP EliteBook", "ThinkPad"]
ACCESSORIES = ["USB hub", "external hard drive", "docking station", "webcam", "headset"]
SERVERS = ["PROD-DB-01", "DEV-APP-01", "STAGING-WEB-01", "BACKUP-01", "MAIL-01"]
DBS = ["MySQL", "PostgreSQL", "Oracle", "MSSQL", "MongoDB"]
SOFTWARES = ["Microsoft Teams", "Zoom", "Adobe Acrobat", "AutoCAD", "Slack", "JIRA", "Confluence"]
KEYS = ["Ctrl", "Alt", "Enter", "Space", "F-keys", "Backspace"]
FILE_TYPES = [".pdf", ".xlsx", ".docx", ".pptx", ".csv"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
COURSES = ["Security Awareness", "GDPR Compliance", "Data Privacy", "Python Basics", "Leadership 101"]
NAMES = ["Alice Johnson", "Bob Smith", "Carol White", "David Brown", "Eve Davis", "Frank Wilson"]
DEPARTMENTS_LIST = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]
SERVICES = ["payment-service", "auth-service", "notification-service", "api-gateway", "data-pipeline"]
PROJECTS = ["ERP Migration", "CRM Integration", "Mobile App", "Data Warehouse", "Security Audit"]
TABLES = ["users", "transactions", "products", "orders", "invoices", "customers"]
USERS = ["john.doe", "jane.smith", "admin.user", "service.account"]
REGIONS = ["North America", "Europe", "APAC", "LATAM"]
COMPANIES = ["Acme Corp", "TechVentures", "GlobalBank", "RetailMax"]
INSTANCES = ["i-0abc123", "vm-prod-01", "node-02"]
CONTAINERS = ["prod-data", "backup-2024", "media-assets"]
PODS = ["api-pod-1", "worker-pod-2", "cron-pod-1"]
BUCKETS = ["company-assets", "user-uploads", "backup-daily"]
ROLES = ["DataPipelineRole", "S3ReadRole", "LambdaExecutionRole"]
VPCS = ["vpc-prod", "vpc-dev", "vpc-staging"]
AMOUNTS = ["$1,250", "$3,400", "$750", "$12,000", "$450"]
INV_NOS = ["INV-2024-001", "INV-2024-089", "INV-2024-234"]
ITEMS = ["laptops", "monitors", "server hardware", "software licenses"]
PERIODS = ["Q1 2024", "Q2 2024", "FY 2024", "March 2024"]
CATEGORIES = ["Travel", "Meals", "Software", "Training", "Office Supplies"]
CODES = ["CC-1001", "CC-2050", "CC-3300"]
IPS = ["192.168.1.100", "10.0.0.45", "172.16.0.100"]
PORTS = ["22", "3389", "8080", "445"]
COUNTRIES = ["Russia", "China", "Unknown", "Vietnam"]
DOMAINS = ["app.company.com", "portal.company.com", "api.company.com"]
CVSS = ["2024-1234", "2023-4567", "2024-8901"]
SENDERS = ["noreply@suspicious.com", "security@fakecompany.net", "hr@phish.io"]
ERRORS = ["NullPointerException", "SegFault", "TimeoutError", "AuthError", "BuildFailed"]
VERSIONS = ["2.4.1", "3.0.0-RC1", "1.9.8", "4.2.0"]
DEPLOYS = ["api-deployment", "frontend-deployment", "worker-deployment"]
CHARTS = ["nginx-ingress", "cert-manager", "prometheus", "grafana"]
MONITORING_TOOLS = ["Grafana", "Datadog", "CloudWatch", "PagerDuty"]
TASKS_OPS = ["install nginx", "configure firewall", "setup cron", "update packages"]
ENVS = ["staging", "UAT", "QA", "production"]
QUARTERS = ["1", "2", "3", "4"]
REPORTS = ["Sales Pipeline Q3", "Revenue Forecast", "Lead Conversion", "Activity Summary"]
FIELDS = ["phone number", "industry", "annual revenue", "custom tag"]
COUNTS = ["15", "28", "47", "103"]
URLS = ["vendor-portal.com", "api.thirdparty.com", "resources.cloud.com"]
DEPTS = ["Marketing", "Engineering", "Sales", "Support"]
DATES = ["2024-01-15", "2024-06-01", "2024-09-30", "2024-12-31"]


def _fill_template(template: str) -> str:
    """Replace template placeholders with random values."""
    replacements = {
        "{device}": random.choice(DEVICES),
        "{location}": random.choice(LOCATIONS),
        "{accessory}": random.choice(ACCESSORIES),
        "{keys}": random.choice(KEYS),
        "{software}": random.choice(SOFTWARES),
        "{file_type}": random.choice(FILE_TYPES),
        "{server}": random.choice(SERVERS),
        "{db}": random.choice(DBS),
        "{table}": random.choice(TABLES),
        "{user}": random.choice(USERS),
        "{instance}": random.choice(INSTANCES),
        "{container}": random.choice(CONTAINERS),
        "{pod}": random.choice(PODS),
        "{bucket}": random.choice(BUCKETS),
        "{role}": random.choice(ROLES),
        "{vpc1}": random.choice(VPCS),
        "{vpc2}": random.choice(VPCS),
        "{service}": random.choice(SERVICES),
        "{project}": random.choice(PROJECTS),
        "{name}": random.choice(NAMES),
        "{date}": random.choice(DATES),
        "{month}": random.choice(MONTHS),
        "{course}": random.choice(COURSES),
        "{department}": random.choice(DEPARTMENTS_LIST),
        "{ip}": random.choice(IPS),
        "{port}": random.choice(PORTS),
        "{country}": random.choice(COUNTRIES),
        "{cve}": random.choice(CVSS),
        "{sender}": random.choice(SENDERS),
        "{domain}": random.choice(DOMAINS),
        "{error}": random.choice(ERRORS),
        "{version}": random.choice(VERSIONS),
        "{deploy}": random.choice(DEPLOYS),
        "{chart}": random.choice(CHARTS),
        "{monitoring_tool}": random.choice(MONITORING_TOOLS),
        "{task}": random.choice(TASKS_OPS),
        "{env}": random.choice(ENVS),
        "{quarter}": random.choice(QUARTERS),
        "{amount}": random.choice(AMOUNTS),
        "{inv_no}": random.choice(INV_NOS),
        "{item}": random.choice(ITEMS),
        "{period}": random.choice(PERIODS),
        "{category}": random.choice(CATEGORIES),
        "{code}": random.choice(CODES),
        "{report}": random.choice(REPORTS),
        "{field}": random.choice(FIELDS),
        "{count}": random.choice(COUNTS),
        "{company}": random.choice(COMPANIES),
        "{region}": random.choice(REGIONS),
        "{url}": random.choice(URLS),
        "{dept}": random.choice(DEPTS),
    }
    for key, val in replacements.items():
        template = template.replace(key, val)
    return template


def _make_title(description: str) -> str:
    """Create a short title from the first sentence of the description."""
    first_sentence = description.split(".")[0]
    return first_sentence[:100].strip()


def generate_tickets(n: int = 10000) -> pd.DataFrame:
    """Generate n realistic IT support tickets."""
    random.seed(42)
    dept_names = list(DEPARTMENTS.keys())
    tickets_per_dept = n // len(dept_names)
    extra = n % len(dept_names)

    records = []
    ticket_id = 1
    base_date = datetime(2023, 1, 1, tzinfo=timezone.utc)

    for i, dept_name in enumerate(dept_names):
        dept_info = DEPARTMENTS[dept_name]
        count = tickets_per_dept + (1 if i < extra else 0)
        templates = dept_info["templates"]

        for j in range(count):
            template = templates[j % len(templates)]
            description = _fill_template(template)
            # Add extra context sentences
            extra_context = random.choice([
                " Please resolve as soon as possible.",
                " This is blocking my work completely.",
                " Urgently need assistance.",
                " This started happening after the weekend.",
                " Multiple users are affected by this issue.",
                " Please escalate if not resolved by EOD.",
                " I have already tried restarting.",
                " This is a recurring issue.",
                "",
                "",
            ])
            description = description + extra_context

            title = _make_title(description)
            priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0]
            status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]

            days_ago = random.randint(0, 365)
            created_at = base_date + timedelta(days=days_ago, hours=random.randint(0, 23))

            records.append({
                "ticket_id": ticket_id,
                "title": title,
                "description": description,
                "department": dept_name,
                "priority": priority,
                "status": status,
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
            ticket_id += 1

    df = pd.DataFrame(records)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df["ticket_id"] = range(1, len(df) + 1)
    return df


def generate_and_save_dataset(output_path: str = None) -> str:
    """Generate and save the dataset to CSV."""
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_path = os.path.join(base_dir, "dataset", "tickets.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = generate_tickets(10000)
    df.to_csv(output_path, index=False)
    print(f"✅ Dataset saved to {output_path} — {len(df)} records, {df['department'].nunique()} departments")
    print(df["department"].value_counts().to_string())
    return output_path


if __name__ == "__main__":
    generate_and_save_dataset()
