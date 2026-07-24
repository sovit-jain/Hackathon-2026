# Deployment Guide - DB Career Navigator

## Quick Fix for Current Issue

You're getting "Unable to create account" because your deployed frontend doesn't know the backend URL. The issue is that `NEXT_PUBLIC_API_URL` must be set at **build time** in Next.js.

### Immediate Steps (Option 1: Using gcloud CLI)

1. **Get your deployed backend URL** (from Cloud Run Console):
   ```
   Backend URL: https://skillbridge-backend-xxxxx-uc.a.run.app
   ```

2. **Rebuild and deploy frontend with correct API URL**:
   ```bash
   cd frontend
   
   # Build locally with backend URL
   NEXT_PUBLIC_API_URL=https://skillbridge-backend-xxxxx-uc.a.run.app npm run build
   
   # Deploy to Cloud Run
   gcloud run deploy skillbridge-frontend \
     --source . \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars NEXT_PUBLIC_API_URL=https://skillbridge-backend-xxxxx-uc.a.run.app \
     --memory 2Gi \
     --cpu 2
   ```

3. **Deploy backend with FRONTEND_URL for CORS**:
   ```bash
   cd backend
   
   FRONTEND_URL=https://skillbridge-frontend-xxxxx-uc.a.run.app \
   ENVIRONMENT=production \
   DATABASE_URL=postgresql://user:pass@cloud-sql-host:5432/dbname \
   OPENAI_API_KEY=sk-... \
   gcloud run deploy skillbridge-backend \
     --source . \
     --region us-central1 \
     --platform managed \
     --timeout 3600 \
     --memory 2Gi \
     --cpu 2 \
     --set-env-vars FRONTEND_URL=${FRONTEND_URL},ENVIRONMENT=production,DATABASE_URL=${DATABASE_URL},OPENAI_API_KEY=${OPENAI_API_KEY}
   ```

### Option 2: Using Cloud Build (Automated)

1. **Update `cloudbuild.yaml`** with your actual URLs:
   ```yaml
   substitutions:
     _BACKEND_URL: 'https://your-backend-xxxxx-uc.a.run.app'
     _FRONTEND_URL: 'https://your-frontend-xxxxx-uc.a.run.app'
     _DATABASE_URL: 'postgresql://...'
     _OPENAI_API_KEY: 'sk-...'
   ```

2. **Submit build to Cloud Build**:
   ```bash
   gcloud builds submit . \
     --config cloudbuild.yaml \
     --substitutions _BACKEND_URL=https://your-backend-url,_FRONTEND_URL=https://your-frontend-url,_DATABASE_URL=postgresql://...,_OPENAI_API_KEY=sk-...
   ```

---

## Environment Variables Checklist

### Backend (Cloud Run Environment Variables)
| Variable | Required | Example |
|---|---|---|
| `ENVIRONMENT` | ✅ | `production` |
| `DATABASE_URL` | ✅ | `postgresql://user:pass@host:5432/db` |
| `FRONTEND_URL` | ✅ | `https://your-frontend.com` |
| `OPENAI_API_KEY` | ✅ | `sk-...` |

### Frontend (Build-Time Only)
| Variable | Required | Example | Set During |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | `https://your-backend.com` | Docker build |

---

## Troubleshooting

### Issue: "Unable to create account" error

**Cause:** Frontend can't reach backend API

**Check:**
1. Open browser DevTools → Network tab → Try signup
2. Look for failed API call to `/api/auth/register`
3. Check the request URL - is it pointing to your backend?
4. Check response headers for CORS errors

**Fix:**
- Verify `NEXT_PUBLIC_API_URL` was passed during build
- Verify backend has `FRONTEND_URL` set to your frontend domain
- Check backend logs: `gcloud run logs read skillbridge-backend --region us-central1`

### Issue: CORS error (from browser console)

**Cause:** Backend CORS not configured for your frontend

**Fix:**
Set backend `FRONTEND_URL` env var to match frontend origin:
```bash
gcloud run services update skillbridge-backend \
  --update-env-vars FRONTEND_URL=https://your-frontend-domain.com \
  --region us-central1
```

### Issue: Blank signup page or API calls failing

**Cause:** `NEXT_PUBLIC_API_URL` is empty at build time

**Fix:**
- Always pass `--build-arg NEXT_PUBLIC_API_URL=<backend-url>` to Docker build
- Or use the Cloud Build automation in `cloudbuild.yaml`

---

## Verification Steps

1. **Frontend is using correct API URL**:
   ```bash
   # View built environment variables in your frontend:
   # Check the .next/static/chunks directory for hardcoded URL
   # Or check browser DevTools Console - it will log API base URL
   ```

2. **Backend accepts frontend origin**:
   ```bash
   gcloud run services describe skillbridge-backend --region us-central1 | grep FRONTEND_URL
   ```

3. **Test signup end-to-end**:
   - Navigate to https://your-frontend.com/signup
   - Fill form and click "Create account"
   - Check browser DevTools → Network → look for POST `/api/auth/register`
   - Should see 200 response (success) not 403/CORS error

---

## Deploy Script (Automated)

Create `deploy.sh`:
```bash
#!/bin/bash

BACKEND_URL="https://skillbridge-backend-xxxxx-uc.a.run.app"
FRONTEND_URL="https://skillbridge-frontend-xxxxx-uc.a.run.app"
DATABASE_URL="postgresql://..."
OPENAI_API_KEY="sk-..."
REGION="us-central1"

echo "🚀 Deploying DB Career Navigator..."

# Frontend
echo "📦 Building frontend with API URL: $BACKEND_URL"
gcloud builds submit ./frontend \
  --region $REGION \
  --config - << EOF
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/\${PROJECT_ID}/skillbridge-frontend', '--build-arg', 'NEXT_PUBLIC_API_URL=$BACKEND_URL', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/\${PROJECT_ID}/skillbridge-frontend']
  - name: 'gcr.io/cloud-builders/run'
    args: ['deploy', 'skillbridge-frontend', '--image', 'gcr.io/\${PROJECT_ID}/skillbridge-frontend', '--region', '$REGION', '--platform', 'managed', '--allow-unauthenticated']
EOF

# Backend
echo "📦 Deploying backend with FRONTEND_URL: $FRONTEND_URL"
gcloud run deploy skillbridge-backend \
  --source ./backend \
  --region $REGION \
  --platform managed \
  --set-env-vars \
    ENVIRONMENT=production,\
    FRONTEND_URL=$FRONTEND_URL,\
    DATABASE_URL=$DATABASE_URL,\
    OPENAI_API_KEY=$OPENAI_API_KEY \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600

echo "✅ Deployment complete!"
echo "Frontend: $FRONTEND_URL"
echo "Backend: $BACKEND_URL"
```

Save and run:
```bash
chmod +x deploy.sh
./deploy.sh
```

