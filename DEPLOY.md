# Deploy Retail Pulse

This project has two deployment surfaces:

1. **The Streamlit dashboard** (`app.py`) — a running Python web app.
2. **The GoDaddy/cPanel landing page** (`deploy/godaddy_static/index.html`) — static HTML that can be uploaded to `public_html`.

## GitHub

The repository should exclude raw Olist CSVs, the local virtualenv, cache files, and local secrets. The deployable app uses:

- `app.py`
- `data_gen.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `scripts/build_olist_data.py`
- `data/*.csv`
- project docs

Recommended repository name:

```text
commerce-leak-studio
```

After GitHub auth is working:

```bash
git init
git add .
git commit -m "Package Retail Pulse dashboard"
gh repo create commerce-leak-studio --private --source=. --remote=origin --push
```

If the repository already exists:

```bash
git remote add origin git@github.com:YOUR_USER/commerce-leak-studio.git
git branch -M main
git push -u origin main
```

## Streamlit Cloud

Use this for the actual dashboard unless GoDaddy has a Python app service that can run a long-lived Streamlit process.

1. Push the repo to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from the GitHub repo.
4. Set main file to `app.py`.
5. Add `OPENAI_API_KEY` in Streamlit secrets only if you want server-side key management.

The current app accepts an OpenAI key in the sidebar, so secrets are optional for demos.

## GoDaddy / cPanel Static Landing Page

The cPanel FTP Accounts documentation says FTP accounts manage website files and that the FTP account directory controls the top-level directory the account can access. For a public website, upload static files to the correct web root, typically `public_html`.

Upload this file:

```text
deploy/godaddy_static/index.html
```

To:

```text
public_html/retaildemo/index.html
```

Then the GoDaddy landing page will live at:

```text
https://YOUR_DOMAIN/retaildemo/
```

The `Launch live demo` and `Open Dashboard` links on that page currently point to:

```text
https://tormin-retail-demo.streamlit.app/
```

## GoDaddy / cPanel Python Hosting Caveat

Basic FTP upload does not run a Streamlit app. Streamlit needs a Python process listening on a port. Most shared cPanel plans only serve static/PHP files from `public_html`.

If GoDaddy/cPanel has **Setup Python App** or **Application Manager** enabled, ask whether it supports long-running Streamlit apps. cPanel Python apps usually run WSGI/Passenger applications, while Streamlit is not a normal WSGI app. If Streamlit cannot run there, use GoDaddy for the landing page and Streamlit Cloud for the dashboard.
