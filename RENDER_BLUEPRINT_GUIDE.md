# Render Blueprint Deployment Guide

## 🚀 Quick Start

### Step 1: Push to Git Repository
```bash
git add render.yaml
git commit -m "Add Render Blueprint configuration"
git push
```

### Step 2: Deploy via Blueprint

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Sign in or create account

2. **Create Blueprint**
   - Click "New +" → "Blueprint"
   - Connect your Git repository (GitHub, GitLab, or Bitbucket)
   - Select the repository containing `render.yaml`

3. **Review Configuration**
   - Render will detect `render.yaml` automatically
   - Review the service configuration
   - Verify settings match your needs

4. **Deploy**
   - Click "Apply" to create the service
   - Render will build and deploy automatically
   - Monitor build logs in the dashboard

## 📋 Blueprint Configuration Details

### Service Configuration

```yaml
services:
  - type: web                    # Web service type
    name: code-extractor-web     # Service name
    runtime: docker              # Docker runtime
    plan: starter                # Pricing plan
    region: oregon               # Deployment region
    dockerfilePath: ./Dockerfile # Path to Dockerfile
    dockerContext: .             # Build context
    healthCheckPath: /           # Health check endpoint
    autoDeploy: true             # Auto-deploy on git push
    branch: main                 # Git branch to deploy
```

### Environment Variables

- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered
- `FLASK_ENV=production`: Sets Flask to production mode
- `PORT`: Automatically set by Render (don't override)

### Plans Available

- **free**: Free tier (spins down after inactivity)
- **starter**: $7/month (always on, 512MB RAM)
- **standard**: $25/month (1GB RAM, better performance)
- **pro**: $85/month (2GB RAM, auto-scaling)

### Regions Available

- **oregon**: US West Coast
- **frankfurt**: Europe
- **singapore**: Asia Pacific
- **ohio**: US East Coast
- **virginia**: US East Coast

## 🔧 Customization

### Change Plan
Edit `render.yaml`:
```yaml
plan: standard  # Change from starter to standard
```

### Change Region
Edit `render.yaml`:
```yaml
region: frankfurt  # Change from oregon to frankfurt
```

### Disable Auto-Deploy
Edit `render.yaml`:
```yaml
autoDeploy: false  # Manual deployments only
```

### Change Branch
Edit `render.yaml`:
```yaml
branch: develop  # Deploy from develop branch
```

## 🌐 Custom Domain Setup

After deployment:

1. **Add Custom Domain**
   - Go to service settings → "Custom Domains"
   - Click "Add Custom Domain"
   - Enter: `codefrom.chat`
   - Also add: `www.codefrom.chat` (optional)

2. **Configure DNS**
   - Render provides DNS records
   - Add CNAME record: `codefrom.chat` → `your-service.onrender.com`
   - Wait for DNS propagation (up to 48 hours)

3. **SSL Certificate**
   - Render automatically provisions SSL via Let's Encrypt
   - HTTPS enabled automatically after DNS propagation

## 📊 Monitoring

- **Logs**: View in Render Dashboard → Service → Logs
- **Metrics**: CPU, Memory, Request count, Response times
- **Alerts**: Set up in service settings

## 🔄 Updates

### Automatic Updates
With `autoDeploy: true`:
- Push to `main` branch → Auto-deploys
- Monitor deployment in dashboard

### Manual Updates
With `autoDeploy: false`:
- Go to service dashboard
- Click "Manual Deploy"
- Select branch/commit

## 🐛 Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all files in repository
- Review build logs for errors

### Service Won't Start
- Verify PORT environment variable (auto-set by Render)
- Check application logs
- Ensure gunicorn is in requirements.txt

### Domain Not Working
- Verify DNS records are correct
- Wait for DNS propagation
- Check SSL certificate status

## ✅ Verification Checklist

- [ ] `render.yaml` is in repository root
- [ ] Dockerfile exists and is valid
- [ ] `requirements.txt` includes gunicorn
- [ ] Git repository is connected to Render
- [ ] Blueprint created successfully
- [ ] Service is running
- [ ] Health check passes
- [ ] Custom domain configured (if applicable)

## 📚 Additional Resources

- [Render Blueprint Documentation](https://render.com/docs/blueprint-spec)
- [Render Docker Guide](https://render.com/docs/docker)
- [Render Environment Variables](https://render.com/docs/environment-variables)

---

**Ready to deploy?** Push your code and create the Blueprint in Render Dashboard!
