# Frontend state machine

This diagram describes the React frontend's current session, route, and audit
behavior. The JWT is stored in localStorage and restored on reload until its expiry.
Sign-out, expiry, or a protected API 401 removes the stored token.

```mermaid
stateDiagram-v2
    [*] --> RestoringSession
    RestoringSession --> Authenticated: valid unexpired stored JWT
    RestoringSession --> Unauthenticated: absent, malformed or expired JWT

    Unauthenticated --> Login: open /login
    Unauthenticated --> Login: request protected route / redirect and retain path
    Login --> Authenticating: submit username and password
    Authenticating --> Authenticated: login succeeds / persist JWT in localStorage
    Authenticating --> Login: login fails / show error
    Login --> Authenticated: already authenticated / redirect to /

    Authenticated --> Workspace: visit intended route or /
    state Workspace {
        [*] --> ResolvingRoute
        ResolvingRoute --> RouteLoading: lazy page chunk is loading
        RouteLoading --> Dashboard: index route loads
        RouteLoading --> CloudAudit: /audit loads
        RouteLoading --> Agents: /agents loads
        RouteLoading --> Findings: /findings loads
        RouteLoading --> ReportDetail: /reports/:assessmentId loads
        RouteLoading --> ReportDetail: /findings/:assessmentId legacy detail link loads
        RouteLoading --> Settings: /settings loads
        ResolvingRoute --> Login: /login / replace with /
        ResolvingRoute --> Dashboard: unknown path / replace with /
        Dashboard --> ResolvingRoute: navigate to another workspace route
        CloudAudit --> ResolvingRoute: navigate to another workspace route
        Agents --> ResolvingRoute: navigate to another workspace route
        Findings --> ResolvingRoute: navigate to another workspace route
        ReportDetail --> ResolvingRoute: navigate to another workspace route
        Settings --> ResolvingRoute: navigate to another workspace route
    }

    CloudAudit --> AuditRunning: submit valid audit request
    AuditRunning --> AuditSucceeded: backend returns response / save latest output and invalidate assessment and identity queries
    AuditRunning --> AuditFailed: request fails / show error
    AuditFailed --> AuditRunning: submit again with valid service selection and accepted region
    AuditSucceeded --> AuditRunning: submit another valid audit request
    AuditSucceeded --> CloudAudit: remain on page
    AuditFailed --> CloudAudit: remain on page

    Authenticated --> Unauthenticated: sign out / clear stored JWT, API token and username
    Authenticated --> Unauthenticated: protected API returns 401 / session-expired event
    Unauthenticated --> Login: redirect to /login
    note right of Authenticated
        Protected routes require an unexpired JWT; the backend verifies its signature.
        Reload restores the token and username. Expiry clears storage.
        A 401 clears the session and redirects to login.
    end note

    note right of ReportDetail
        Assessment timestamps are returned as UTC and displayed in
        India Standard Time (IST, Asia/Kolkata, UTC+05:30).
    end note

    note right of AuditRunning
        Backend agent steps run sequentially but are not streamed.
        The UI shows one running state until the complete response arrives.
    end note
```

## State and transition notes

- The login route is public. Protected routes redirect unauthenticated visitors
  to `/login` and retain the requested location for post-login navigation.
- The application displays a shared loading state while a lazy route chunk is
  loading. Unknown paths redirect to the dashboard.
- On audit submission, the frontend requires at least one selected service and
  confirmation of the backend-configured AWS region before sending a request.
- Successful audit output is put in the `latest-audit` query cache. It is not
  persisted across a browser reload; the `latest-audit` query itself is disabled
  until the current session supplies data.
- Assessment and AWS identity query data refresh after a successful audit.
  Query-backed pages can independently display loading, error, empty, and
  loaded states.
- API failures remain on the current page with an error message, except for
  `401` responses, which expire the session and redirect to login.
