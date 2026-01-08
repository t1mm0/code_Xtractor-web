# Quick Deploy to Render.com

## 🚀 Fast Deployment Steps

### 1. Push to Git Repository
```bash
git add .
git commit -m "Add Docker deployment configuration"
git push
```

### 2. Deploy on Render.com

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Configure:
   - **Name**: `code-extractor-web`
   - **Runtime**: Docker
   - **Dockerfile Path**: `Dockerfile`
   - **Plan**: Starter ($7/mo) or Standard ($25/mo)
5. Click "Create Web Service"

### 3. Add Custom Domain

1. In service settings → "Custom Domains"
2. Add: `codefrom.chat`
3. Update DNS records as shown in Render dashboard
4. Wait for SSL certificate (automatic)

### 4. Done! 🎉

Your app will be live at: **https://codefrom.chat**

---

For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)
