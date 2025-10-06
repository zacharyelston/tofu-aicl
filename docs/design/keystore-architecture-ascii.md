# AICL Keystore Architecture - Visual Diagrams

## Main Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AICL KEYSTORE ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  AICL Engine    │
│  & Keystore     │ ──────┐
│  Manager        │       │
└─────────────────┘       │
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│     PROVIDER LAYER      │                                     │
│                         ▼                                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ Azure Key Vault │ │ AWS Secrets Mgr │ │ Google Secrets  │ │
│  │                 │ │                 │ │ Manager         │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│                                                              │
│  ┌─────────────────┐ ┌─────────────────┐                    │
│  │ Local .env File │ │ Environment     │                    │
│  │                 │ │ Variables       │                    │
│  └─────────────────┘ └─────────────────┘                    │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION LAYER                         │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐ │
│  │keystore.yaml│ │.env.template│ │     terraform/              │ │
│  │             │ │             │ │  ├── azure/                 │ │
│  │             │ │             │ │  ├── aws/                   │ │
│  │             │ │             │ │  └── gcp/                   │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  LLM SESSION PROTECTION                        │
│                                                                 │
│  🚨 CRITICAL: Prevent Simulation Fallbacks                     │
│  ✅ Validation Rules                                           │
│  📋 Error Guidance                                             │
│  🛡️  Session Instructions                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Fallback Strategy Flow

```
┌─────────────┐
│ Key Request │
└──────┬──────┘
       │
       ▼
┌──────────────────┐     YES    ┌─────────────────┐
│ Primary Provider │ ─────────► │ Retrieve from   │
│ Available?       │            │ Primary         │
└──────┬───────────┘            └─────────┬───────┘
       │ NO                               │
       ▼                                  │
┌──────────────────┐     YES    ┌─────────────────┐
│ Secondary        │ ─────────► │ Retrieve from   │
│ Provider         │            │ Secondary       │
│ Available?       │            └─────────┬───────┘
└──────┬───────────┘                      │
       │ NO                               │
       ▼                                  │
┌──────────────────┐     YES    ┌─────────────────┐
│ Local .env       │ ─────────► │ Load from       │
│ Available?       │            │ .env            │
└──────┬───────────┘            └─────────┬───────┘
       │ NO                               │
       ▼                                  │
┌──────────────────┐     YES    ┌─────────────────┐
│ Environment      │ ─────────► │ Load from       │
│ Variables?       │            │ ENV             │
└──────┬───────────┘            └─────────┬───────┘
       │ NO                               │
       ▼                                  │
┌──────────────────┐                      │
│ FAIL with Clear  │                      │
│ Error Message    │                      │
└──────┬───────────┘                      │
       │                                  │
       ▼                                  │
┌──────────────────┐                      │
│ Show LLM         │                      │
│ Instructions     │                      │
└──────┬───────────┘                      │
       │                                  │
       ▼                                  │
┌──────────────────┐                      │
│ Prevent          │                      │
│ Simulation       │                      │
│ Fallback         │                      │
└──────────────────┘                      │
                                          │
                    ┌─────────────────────┘
                    │
                    ▼
              ┌─────────────┐
              │ Cache       │
              │ Result      │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ Return Key  │
              └─────────────┘
```

## Provider Priority Matrix

```
┌─────────────────────┬─────────────┬─────────────┬──────────┐
│ Provider            │ Effort      │ Adoption    │ Priority │
├─────────────────────┼─────────────┼─────────────┼──────────┤
│ Azure Key Vault     │ Medium      │ High        │ P0 🔥    │
│ Local .env          │ Low         │ High        │ P0 🔥    │
│ AWS Secrets Manager │ Medium      │ Medium      │ P1       │
│ Environment Vars    │ Low         │ Medium      │ P1       │
│ Google Secret Mgr   │ Medium      │ Low         │ P2       │
└─────────────────────┴─────────────┴─────────────┴──────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYERS                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ENCRYPTION AT REST                                             │
│ ├── Azure Key Vault: Hardware Security Modules (HSM)          │
│ ├── AWS Secrets: AES-256 with AWS KMS                         │
│ ├── Google Secrets: AES-256 with Google KMS                   │
│ └── Local .env: File system permissions (600)                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ENCRYPTION IN TRANSIT                                          │
│ ├── TLS 1.3 for all cloud communications                      │
│ ├── Certificate pinning for critical connections              │
│ └── Mutual TLS for service-to-service communication           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ACCESS CONTROL                                                 │
│ ├── Azure: RBAC + Managed Identity                            │
│ ├── AWS: IAM Policies + Least Privilege                       │
│ ├── Google: Service Accounts + IAM                            │
│ └── Local: File system + User permissions                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ AUDIT & MONITORING                                             │
│ ├── All key access logged with timestamp                      │
│ ├── User/session identification                               │
│ ├── Success/failure tracking                                  │
│ └── Anomaly detection for unusual patterns                    │
└─────────────────────────────────────────────────────────────────┘
```
