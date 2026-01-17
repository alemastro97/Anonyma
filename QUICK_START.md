# Anonyma - Quick Start Guide

**Deploy Anonyma in 2 minutes with one command.**

---

## ⚡ One-Command Setup

```bash
./setup.sh
```

That's it! The script will:
1. Check Docker installation
2. Generate secure secrets
3. Create `.env` configuration
4. Build and start all services
5. Wait for services to be ready

---

## 📍 Access

After setup completes:

- **Frontend**: http://localhost
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🔐 Login

### Admin (Unlimited)
```
Username: admin
Password: admin123  ⚠️ CHANGE THIS!
```

### Demo Mode (50/day)
Click "Try Demo Mode (Limited)" on login page

### Register New Account
Create account at `/register` → gets demo role

---

## 🛠️ Common Commands

### View Logs
```bash
# Docker Compose v2 (recommended)
docker compose -f docker-compose.full.yml logs -f
docker compose -f docker-compose.full.yml logs -f api  # API only

# Or Docker Compose v1
docker-compose -f docker-compose.full.yml logs -f
```

### Stop Services
```bash
docker compose -f docker-compose.full.yml down
# Or: docker-compose -f docker-compose.full.yml down
```

### Restart Services
```bash
docker compose -f docker-compose.full.yml restart
```

### Rebuild After Changes
```bash
docker compose -f docker-compose.full.yml up -d --build
```

### Check Status
```bash
docker compose -f docker-compose.full.yml ps
```

**Note**: Use `docker compose` (v2) or `docker-compose` (v1) based on your Docker version.

---

## 📦 What's Running

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 3000 (internal) | React UI |
| **API** | 8000 (internal) | FastAPI backend |
| **Nginx** | 80 | Reverse proxy |
| **PostgreSQL** | 5432 (internal) | User database |
| **Redis** | 6379 (internal) | Job storage |

All services run in Docker and are accessible via Nginx on port 80.

---

## 🎯 Features Available

### Text Anonymization
- Multiple modes: Redact, Substitute, Visual Redact
- Languages: Italian, English
- AI detection: Presidio + Flair NER

### Document Processing
- Formats: PDF, Word, Excel, PowerPoint, Images, Email
- Drag & drop upload
- Real-time progress tracking

### Admin Dashboard (Admin only)
- User management
- Role changes
- Quota resets
- System statistics

### Pricing & Payments (Optional)
- Stripe integration for premium subscriptions
- Automatic role upgrades

---

## ⚙️ Configuration

### Edit `.env` file:

**Required Changes for Production:**
```bash
DEFAULT_ADMIN_PASSWORD=<your_secure_password>
```

**Optional - Stripe Payments:**
```bash
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_PREMIUM=price_xxx
```

**Optional - Email Notifications:**
```bash
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your_password
```

After changing `.env`, restart services:
```bash
docker compose -f docker-compose.full.yml restart
```

---

## 📊 User Roles & Quotas

| Role | Daily | Monthly | Cost |
|------|-------|---------|------|
| **Admin** | Unlimited | Unlimited | - |
| **Premium** | 1,000 | 10,000 | $29/mo |
| **Demo** | 50 | 500 | Free |

Quotas reset automatically:
- Daily: Midnight UTC
- Monthly: 1st of each month

---

## 🔧 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker compose -f docker-compose.full.yml logs

# Rebuild clean
docker compose -f docker-compose.full.yml down -v
./setup.sh
```

### Can't Login
```bash
# Check API is running
curl http://localhost:8000/health

# View API logs
docker compose -f docker-compose.full.yml logs api
```

### Frontend Not Loading
```bash
# Check Nginx
docker compose -f docker-compose.full.yml logs nginx

# Rebuild frontend
docker compose -f docker-compose.full.yml up -d --build frontend
```

### Reset Admin Password
```bash
# Connect to database
docker compose -f docker-compose.full.yml exec postgres psql -U anonyma anonyma

# Reset password (in psql)
UPDATE users SET password_hash = '$2b$12$...' WHERE username = 'admin';
```

---

## 📚 Documentation

- **DEPLOYMENT_GUIDE.md** - Full deployment guide
- **SYSTEM_COMPLETE.md** - System architecture
- **AUTHENTICATION_COMPLETE.md** - Auth system details

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Change `DEFAULT_ADMIN_PASSWORD` in `.env`
- [ ] Generate new `JWT_SECRET`
- [ ] Set `ANONYMA_DEBUG=false`
- [ ] Configure domain in `REACT_APP_API_URL`
- [ ] Set up SSL/HTTPS certificates
- [ ] Update CORS in `packages/anonyma_api/main.py`
- [ ] Configure Stripe keys (if using payments)
- [ ] Configure SMTP (if using emails)
- [ ] Set up backups for PostgreSQL
- [ ] Configure monitoring/alerts

---

## 📞 Support

**Logs**:
```bash
docker compose -f docker-compose.full.yml logs -f
```

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Database**:
```bash
docker compose -f docker-compose.full.yml exec postgres psql -U anonyma anonyma
```

---

## 🎉 That's It!

You're ready to use Anonyma. Visit http://localhost and start anonymizing!

**Need help?** Check the full documentation in `DEPLOYMENT_GUIDE.md`

---

**Version**: 1.0.0
**Last Updated**: 2026-01-17
