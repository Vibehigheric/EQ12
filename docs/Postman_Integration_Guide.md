# EQ12 Postman Integration Guide

Use this workflow to explore and debug the X API / X Ads API endpoints with Postman while keeping credentials in sync with the EQ12 stack.

## 1. Export environment variables from EQ12

```
cd C:\EQ12
powershell -ExecutionPolicy Bypass -File .\scripts\export_postman_environment.ps1
```

- The helper captures process, user, and machine environment variables such as `X_CONSUMER_KEY`, `X_ACCESS_TOKEN`, `X_BEARER_TOKEN`, and X Ads client secrets.
- It writes `configs\postman\EQ12_X_API_v2.postman_environment.json` (or the path you pass via `-OutputPath`).
- Empty values mean the variable is not configured yet. Set them in your shell profile or secrets manager and rerun the export when ready.

To generate a custom file name or keep the JSON in another workspace:

```
powershell -ExecutionPolicy Bypass -File .\scripts\export_postman_environment.ps1 ^
    -OutputPath 'D:\postman\eq12_ads_environment.json' ^
    -EnvironmentName 'EQ12 Ads Sandbox'
```

## 2. Import the environment into Postman

1. Open Postman and select **Environments -> Import** (top-right gear icon).
2. Choose the generated `*.postman_environment.json` file.
3. With the environment selected, confirm that variables like `consumer_key` and `bearer_token` are populated.

## 3. Load EQ12's Postman collections

- X API v2 collection: exposes timelines, tweet lookup, and media endpoints.
- X Ads API collection: exposes campaigns, line items, creatives, and analytics.

Use **Import -> Link** in Postman with the official URLs, or load the `.json` artifacts if you already synced them locally.

## 4. Make a test request

1. Select an endpoint (for example, **X API v2 -> Post Lookup -> Single Post**).
2. On the **Params** tab, enable desired query fields (`tweet.fields`, `expansions`) and provide a real Post ID under **Path Variables -> id**.
3. Click **Send** and verify the HTTP response payload.

## 5. Generate OAuth 2.0 user tokens (optional)

- Open the collection's **Auth** tab and change the type to **OAuth 2.0**.
- Update the configuration with your client ID, client secret, redirect URI, and scopes (for example, `tweet.read users.read offline.access`).
- Choose **Authorization Code (With PKCE)** if you are using public clients.
- Click **Get New Access Token**, authorize the app, and then **Use Token** for delegated requests.

## 6. Convert a request into code

After confirming the request works, click **Code** in Postman to export a ready-to-run snippet (Python, Node.js, etc.). Drop the snippet into EQ12 automation scripts when you need a reproducible test fixture.

---

### Troubleshooting

| Issue | Fix |
| ----- | --- |
| "Missing values for ..." warning after running the export script | Define the corresponding environment variables (for example, `setx X_CONSUMER_KEY your_key`) and rerun the exporter. |
| 401 Unauthorized from X endpoints | Ensure the `bearer_token` is valid and matches the project; regenerate via the X developer portal if required. |
| OAuth 2.0 callback mismatch | Update the redirect URI in Postman to match the app settings under the X developer portal. |
| Need fresh Ads account IDs | Add `X_ADS_ACCOUNT_ID` to your environment so the exporter persists it for Postman. |

### Related tooling

- `scripts\export_postman_environment.ps1` ? keeps Postman environments aligned with EQ12 secrets.
- `Eq12CliMainProgram.vb` ? CLI routes for metrics, X Ads operations, and governance tools.
- `Eq12CliGitHubExtensionEnhanced.vb` ? contains the metrics-sync/metrics-report/metrics-diff implementations if you want to replicate calls outside Postman.

Keep the environment JSON out of version control; treat it like any other credential artifact.
