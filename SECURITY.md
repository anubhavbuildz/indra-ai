# Security policy

## Supported versions

Only the latest development state on the default branch is currently
supported. No stable release or security maintenance window has been
announced.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to **[MAINTAINER SECURITY
CONTACT ADDRESS]**. Replace this placeholder with a monitored private contact
before public release. Do not file an issue for an unpatched vulnerability
or publish exploit details before coordinating disclosure.

Include:

- A concise description and affected version/commit.
- The impact and conditions needed to reproduce it.
- A minimal proof of concept or logs with secrets removed.
- Any suggested mitigation.

Never send actual API keys, AWS credentials, cloud account secrets, or customer
data. The project has no committed response-time
promise.

## Security boundaries

The scaffold does not implement authentication, authorization, tenant
isolation, or a complete audit workflow. Chat runs read-only AWS checks and
provides point-in-time decision support, not a certification or guarantee of
security.
