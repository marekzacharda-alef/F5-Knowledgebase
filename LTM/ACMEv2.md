# ACMEv2 Certificate Automation on F5 BIG-IP 21.1 (Let's Encrypt)

> **Source / credit:** Based on the DevCentral article
> [Automatic Certificate Management with ACMEv2 in F5 BIG-IP](https://community.f5.com/t/automatic-certificate-management-with-acmev2-in-f5-big-ip/77193)
> by *mendes* and its community discussion. This is an independent summary written as working notes. Refer to the original article for screenshots.
>
> **Official docs:** [SSL Certificate Management – ACME Provider Setup (BIG-IP 21.1.0)](https://techdocs.f5.com/en-us/bigip-21-1-0/big-ip-system-ssl-administration/ssl-certificate-management.html#acme-provider-setup)

Native ACMEv2 support arrived with **BIG-IP 21.1.0** (GA May 2026). It lets BIG-IP order and renew certificates directly from an ACME CA such as Let's Encrypt, with no external scripts.

`example.com` is used as a placeholder domain throughout.

---

## Overview

| Component | Purpose |
|---|---|
| DNS Resolver | Resolves the CA's ACME endpoints |
| Internal Proxy | Carries `keymgmtd` traffic to the CA |
| Account key (self-signed cert) | Identifies the BIG-IP as an ACME account |
| ACME Provider | Binds CA directory URL, proxy, account key, and contact |
| HTTP (port 80) virtual server | Answers `http-01` challenges |
| Certificate order | Requests the cert and renews it automatically |

---

## 1. Prerequisites

### 1.1 DNS Resolver
Create or reuse a BIG-IP DNS Resolver that can reach the internet, or at least resolve the CA's ACME hostnames. The built-in BIG-IP resolver works.

### 1.2 Internal Proxy
Create an **Internal Proxy** object and reference the DNS Resolver above. The ACME Provider requires it even if you don't use an upstream proxy server.

- **Direct internet access:** leave **Use Proxy Server** unchecked.
- **Via corporate proxy:** enable it and point it to your proxy.

> ⚠️ **Routing gotcha:** `keymgmtd` sends requests through the internal proxy listener (port `39443`), and traffic egresses via the **TMM routing table, not the management interface**. If TMM has no route to the internet, account creation fails (see [Troubleshooting](#5-troubleshooting)). A default route (`0.0.0.0/0`) via the gateway behind your egress self-IP is the usual fix.

### 1.3 Account key
Create a **self-signed certificate/key**. ACMEv2 uses it as the device's account identity.

- Subject Alternative Name: not required
- Common Name: a contact e-mail address is recommended

---

## 2. Create the ACME Provider

| Field | Value |
|---|---|
| Name | e.g. `acme_letsencrypt` |
| Internal Proxy | The proxy from step 1.2 |
| CA Certificate | `ca-bundle.crt` (default) works for Let's Encrypt |
| Directory URL | `https://acme-v02.api.letsencrypt.org/directory` |
| Account Key | The self-signed cert/key from step 1.3 |
| Contacts | **Must be a URL** → `mailto:you@example.com` |
| Terms and Conditions | ✅ |
| Create Account | ✅ |

> 💡 For testing, consider the Let's Encrypt **staging** directory (`https://acme-staging-v02.api.letsencrypt.org/directory`) to avoid production rate limits.

Save the provider and wait. **Account Status** should change to **Valid**.

---

## 3. Prepare the HTTP-01 challenge listener

Let's Encrypt validates ownership by requesting:

```
http://<your-domain>/.well-known/acme-challenge/<TOKEN>
```

Requirements:

1. A public DNS **A record** for the domain pointing to an IP that reaches BIG-IP (directly or via NAT).
2. A **virtual server on port 80** at that address, configured to respond to ACME challenges as described in the official docs.

> Each HTTPS virtual server whose certificate you want ACME-managed needs a reachable port 80 listener for that hostname, because `http-01` always validates over HTTP.

### Optional: redirect everything except challenges to HTTPS

Use `starts_with` rather than an exact match. Challenge requests include a token after the path, so an exact-match comparison redirects them and breaks validation.

```tcl
when HTTP_REQUEST {
    # Let ACME http-01 challenges through; redirect all other traffic to HTTPS
    if { not ([HTTP::uri] starts_with "/.well-known/acme-challenge/") } {
        HTTP::redirect "https://[getfield [HTTP::host] ":" 1][HTTP::uri]"
    }
}
```

*(The community thread reports the official docs example was later corrected to the same logic.)*

---

## 4. Order the certificate

1. Create a new certificate order that uses the ACME Provider and lists the domain(s).
2. Watch the **Key** tab until it shows the certificate was issued.
3. Confirm the certificate and chain now exist in the SSL certificate list.
4. Monitor the provider's **statistics** page for activity and errors.

### Use the certificate on a virtual server
Reference the ACME-managed cert, key, and chain in a **Client SSL profile** and attach it to the HTTPS virtual server, as you would any other certificate. Renewed certificates update in place, so the profile keeps working without changes.

### Renewal
Community feedback reports that auto-renewal begins **about 14 days before expiry** and keeps retrying on failure. Verify this against official documentation for your version, especially for short-lived certificates (≤ 7 days).

---

## 5. Troubleshooting

### Account Status = `Error`, `curl_code=56`
Typical log lines in `/var/log/ltm`:

```
Failed to get ACME directory listing from https://acme-v02.api.letsencrypt.org/directory. curl_code=56,response_code=0 ...
Cannot take account action as directory listing is invalid
```

**Cause:** TMM can't reach the CA, usually because no route exists.
**Fix:** add a TMM route to the internet (a default route via your egress gateway). Routing only to the DNS server is not enough.

### Enable debug logging for `keymgmtd`

```bash
# enable
tmsh modify sys db log.keymgmtd.level value debug

# revert
tmsh modify sys db log.keymgmtd.level value notice
```

### Challenge fails but account is valid
- Check that the domain's A record resolves publicly to the port 80 listener.
- Check that no iRule or policy redirects `/.well-known/acme-challenge/*`.
- Check that no firewall in front of BIG-IP blocks inbound TCP/80.

---

## 6. Known limitations / open questions (as of the source discussion)

- **`http-01` only.** No native `dns-01` challenge support, so **no wildcard certificates** yet. External ACME scripts remain an option where DNS validation is needed.
- **AS3 / non-Common partitions.** How ACME-managed certs fit AS3-deployed applications in their own partitions was raised but not answered in the thread.

---

## References

- DevCentral article (original): <https://community.f5.com/t/automatic-certificate-management-with-acmev2-in-f5-big-ip/77193>
- BIG-IP 21.1.0 new features: <https://techdocs.f5.com/en-us/bigip-21-1-0/big-ip-release-notes/big-ip-new-features.html#general>
- BIG-IP 21.1.0 SSL Certificate Management: <https://techdocs.f5.com/en-us/bigip-21-1-0/big-ip-system-ssl-administration/ssl-certificate-management.html#acme-provider-setup>
- Let's Encrypt docs: <https://letsencrypt.org/docs/>
