# Deployment Guide for Render.com

## 🚀 Deploying to Render.com with Docker

This guide will help you deploy the Code Block Extractor web application to Render.com using Docker.

### Prerequisites

1. A Render.com account (sign up at https://render.com)
2. Your domain `codefrom.chat` registered and configured
3. Git repository with your code

### Quick Deploy Steps

#### Option 1: Using Render Dashboard (Recommended)

1. **Log in to Render Dashboard**
   - Go to https://dashboard.render.com
   - Sign in or create an account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository (GitHub, GitLab, or Bitbucket)
   - Select the repository containing this code

3. **Configure Service**
   - **Name**: `code-extractor-web`
   - **Region**: Choose closest to your users (e.g., Oregon, Frankfurt, Singapore)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or set if code is in subdirectory)
   - **Runtime**: Select "Docker"
   - **Dockerfile Path**: `Dockerfile`
   - **Docker Context**: `.` (root)

4. **Environment Variables**
   - Render automatically sets `PORT` environment variable
   - No additional environment variables required for basic deployment

5. **Plan Selection**
   - **Free**: For testing (spins down after inactivity)
   - **Starter**: $7/month (always on, 512MB RAM)
   - **Standard**: $25/month (1GB RAM, better performance)
   - **Pro**: $85/month (2GB RAM, auto-scaling)

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your Docker container
   - Monitor the build logs

#### Option 2: Using render.yaml (Infrastructure as Code)

1. **Push render.yaml to Repository**
   - The `render.yaml` file is already configured
   - Commit and push to your repository

2. **Create Blueprint**
   - In Render Dashboard, click "New +" → "Blueprint"
   - Connect your repository
   - Render will detect `render.yaml` and create services automatically

### Custom Domain Setup (codefrom.chat)

1. **Add Custom Domain**
   - In your service settings, go to "Custom Domains"
   - Click "Add Custom Domain"
   - Enter: `codefrom.chat`
   - Also add: `www.codefrom.chat` (optional)

2. **Configure DNS**
   - Render will provide DNS records to add
   - Add CNAME record pointing to your Render service
   - Example: `codefrom.chat` → `your-service.onrender.com`

3. **SSL Certificate**
   - Render automatically provisions SSL certificates via Let's Encrypt
   - HTTPS will be enabled automatically after DNS propagation

### Environment Variables

The application uses these environment variables:

- `PORT`: Automatically set by Render (don't override)
- `FLASK_ENV`: Set to `production` (default) or `development` for debug mode
- `DEBUG`: Set to `true` to enable debug mode (not recommended for production)

### Health Checks

- **Path**: `/` (root endpoint)
- **Interval**: Render checks every 30 seconds
- **Timeout**: 10 seconds

### Monitoring

- View logs in Render Dashboard → Your Service → Logs
- Monitor metrics: CPU, Memory, Request count, Response times
- Set up alerts for errors or high latency

### Scaling

For production traffic, consider:

1. **Upgrade Plan**: Move to Standard or Pro plan
2. **Auto-scaling**: Available on Pro plan
3. **Worker Processes**: Adjust `--workers` in Dockerfile CMD if needed

### Troubleshooting

#### Build Fails
- Check Dockerfile syntax
- Verify all files are in repository
- Check build logs for specific errors

#### Service Won't Start
- Verify PORT environment variable is set
- Check application logs for errors
- Ensure gunicorn is installed (in requirements.txt)

#### Domain Not Working
- Verify DNS records are correct
- Wait for DNS propagation (can take up to 48 hours)
- Check SSL certificate status in Render dashboard

#### High Memory Usage
- Reduce `--workers` in Dockerfile CMD
- Upgrade to plan with more RAM
- Optimize application code

### Local Testing

Test the Docker container locally before deploying:

```bash
# Build the image
docker build -t code-extractor .

# Run the container
docker run -p 5000:5000 -e PORT=5000 code-extractor

# Test in browser
open http://localhost:5000
```

### Production Checklist

- [ ] Set `FLASK_ENV=production` (or remove DEBUG env var)
- [ ] Use Standard or Pro plan for production
- [ ] Configure custom domain (codefrom.chat)
- [ ] Set up monitoring and alerts
- [ ] Review and adjust resource limits
- [ ] Test health checks
- [ ] Configure backup/restore if needed
- [ ] Set up CI/CD for automatic deployments

### Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Application Issues: Check logs in Render Dashboard

---

**Last Updated**: 2024-12-19
**Domain**: https://codefrom.chat
