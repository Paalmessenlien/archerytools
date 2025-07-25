# SSL Certificate Directory

This directory is for SSL certificates when running in production mode.

## Development

For development, the nginx configuration serves HTTP only on port 80.

## Production

For production deployment with SSL:

1. **Obtain SSL certificates** (recommended method):
```bash
# Using Let's Encrypt
sudo certbot certonly --standalone \
  -d archerytool.online \
  -d www.archerytool.online \
  --email admin@archerytool.online \
  --agree-tos
```

2. **Copy certificates to this directory**:
```bash
sudo cp /etc/letsencrypt/live/archerytool.online/fullchain.pem ./deploy/ssl/
sudo cp /etc/letsencrypt/live/archerytool.online/privkey.pem ./deploy/ssl/
sudo cp /etc/letsencrypt/live/archerytool.online/chain.pem ./deploy/ssl/
sudo chown $USER:$USER ./deploy/ssl/*.pem
```

3. **Enable HTTPS configuration**:
   - Uncomment the HTTPS server block in `./deploy/nginx/sites/default.conf`
   - Update the main HTTP server to redirect to HTTPS

4. **Restart nginx container**:
```bash
docker-compose restart nginx
```

## Certificate Files

- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key
- `chain.pem` - Certificate authority chain

## Auto-renewal

Set up auto-renewal with cron:
```bash
# Add to crontab
0 12 * * * /usr/bin/certbot renew --quiet --post-hook "docker-compose restart nginx"
```