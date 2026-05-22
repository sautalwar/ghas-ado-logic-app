# ADO Connection Setup in Make.com

## Overview

Make.com needs to authenticate with Azure DevOps to create and update work items. There are two authentication methods available.

---

## Option A: Personal Access Token (PAT) — Recommended

### Step 1: Create ADO PAT

1. Go to **Azure DevOps** → click your profile icon (top-right) → **Personal access tokens**
2. Click **"+ New Token"**
3. Configure:
   - **Name:** `Make.com GHAzDO Integration`
   - **Organization:** Select your organization
   - **Expiration:** Choose appropriate duration (max 1 year)
   - **Scopes:** Select **Custom defined**, then enable:
     - ✅ **Work Items** → Read & Write
     - ✅ **Project and Team** → Read
4. Click **"Create"**
5. **Copy the PAT immediately** — it won't be shown again

> ⚠️ **Security:** Store the PAT securely. Set a calendar reminder to rotate it before expiration.

### Step 2: Configure ADO Connection in Make.com

1. In your Make.com scenario, click any **Azure DevOps module**
2. Click the **"Add"** button next to the Connection dropdown
3. Fill in:
   - **Connection name:** `ADO - GHAzDO Integration`
   - **Connection type:** `Personal Access Token`
   - **Organization name:** Your org name (just `my-org`, not the full URL)
   - **Personal Access Token:** Paste the PAT from Step 1
4. Click **"Save"**
5. Make.com will test the connection — you should see a green checkmark

### Step 3: Configure PAT for HTTP Modules (WIQL Queries)

The HTTP modules (for WIQL dedup/search) need the PAT in Base64 format:

1. In your Make.com scenario, click the **gear icon** (scenario settings)
2. Go to **Variables** tab
3. Add a new variable:
   - **Name:** `adoPat`
   - **Value:** Your PAT (plain text — Make.com encrypts it)
4. Add another variable:
   - **Name:** `adoOrganization`
   - **Value:** Your org name
5. Add another variable:
   - **Name:** `adoProject`
   - **Value:** Your project name

In the HTTP module headers, set Authorization to:
```
Basic {{base64(join(array(emptystring; variables.adoPat); ":"))}}
```

Or use the simpler format if Make.com supports direct concatenation:
```
Basic {{base64(":" + variables.adoPat)}}
```

---

## Option B: OAuth 2.0

> **Note:** OAuth is more secure (no PAT to manage) but requires an Azure AD app registration.

### Step 1: Register Azure AD Application

1. Go to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **"+ New registration"**
3. Configure:
   - **Name:** `Make.com ADO Integration`
   - **Redirect URI:** `https://www.integromat.com/oauth/cb/azure-devops` (Make.com's callback URL)
4. After creation, note the **Application (client) ID** and **Directory (tenant) ID**
5. Go to **Certificates & secrets** → **"+ New client secret"**
6. Copy the **secret value**
7. Go to **API permissions** → **"+ Add a permission"** → **Azure DevOps** → **user_impersonation**

### Step 2: Configure in Make.com

1. In the ADO module, choose **"OAuth 2.0"** connection type
2. Enter the Client ID, Client Secret, and Tenant ID
3. Click **"Save"** — you'll be redirected to Microsoft login
4. Sign in and grant permissions

---

## Recommended Approach

**Use PAT (Option A)** for simplicity:
- Faster to set up (5 minutes vs 15 minutes)
- No Azure AD app registration required
- Works immediately
- Only downside: PAT expires and needs rotation

**Use OAuth (Option B)** if:
- Your organization requires OAuth/OIDC
- You want to avoid PAT management
- You have Azure AD admin access

---

## Verifying the Connection

After setup, test the connection:

1. Open any Azure DevOps module in your scenario
2. Select your connection from the dropdown
3. Try selecting Organization → should list your orgs
4. Try selecting Project → should list your projects
5. If either fails, check:
   - PAT scopes are correct
   - PAT hasn't expired
   - Organization name is correct (case-sensitive)
