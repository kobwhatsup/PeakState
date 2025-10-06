# 🔒 Security Policy

## ⚠️ Critical Security Rules

### **NEVER commit these to Git:**

1. **API Keys**
   - ❌ OpenAI API keys (`sk-proj-...`)
   - ❌ Anthropic API keys (`sk-ant-api03-...`)
   - ❌ Any cloud provider keys (AWS, GCP, Azure)

2. **Credentials**
   - ❌ Database passwords
   - ❌ JWT secret keys
   - ❌ Encryption keys
   - ❌ Service account tokens

3. **Configuration Files**
   - ❌ `.env` files (use `.env.example` instead)
   - ❌ `secrets/` directory contents
   - ❌ SSL certificates and private keys

4. **Personal Data**
   - ❌ User data exports
   - ❌ Health data samples
   - ❌ Test data with real PII

---

## ✅ Security Best Practices

### 1. Use Environment Variables

**Good** ✅:
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
```

**Bad** ❌:
```python
api_key = "sk-proj-abc123..."  # NEVER DO THIS
```

### 2. Use `.env.example` for Documentation

```bash
# .env.example - Safe to commit
OPENAI_API_KEY=sk-proj-your-key-here

# .env - NEVER commit this
OPENAI_API_KEY=sk-proj-nRlxa...
```

### 3. Pre-commit Hook

This project has a pre-commit hook that scans for secrets. If triggered:

```
❌ SECRET DETECTED IN STAGED FILES
⚠️  COMMIT BLOCKED FOR SECURITY
```

**Fix**: Remove the secret and use environment variables instead.

### 4. Rotate Keys After Exposure

If a key is accidentally committed:

1. **Immediately revoke** the exposed key:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys

2. **Generate new key** and update `.env`

3. **Clean Git history**:
   ```bash
   # Option 1: Rewrite history (if just committed)
   git reset --soft HEAD~1
   git reset HEAD <file>
   # Remove secret from file
   git add <file>
   git commit --amend
   git push --force

   # Option 2: Use git-filter-repo for old commits
   pip install git-filter-repo
   git-filter-repo --invert-paths --path <file-with-secret>
   ```

4. **Verify cleaning**:
   ```bash
   git log --all --full-history -- <file>
   git grep "sk-proj-" $(git rev-list --all)
   ```

---

## 🛡️ Security Tools

### Installed Protection

1. **Pre-commit Hook** (`.git/hooks/pre-commit`)
   - Blocks commits with API keys
   - Scans for common secret patterns
   - Runs automatically on every commit

2. **.gitignore**
   - Excludes `.env`, `secrets/`, `*.key`
   - Prevents accidental staging

### Recommended Tools

```bash
# Install git-secrets (AWS Labs)
brew install git-secrets
git secrets --install
git secrets --scan

# Install gitleaks (more comprehensive)
brew install gitleaks
gitleaks detect --source . --verbose

# Install detect-secrets (Yelp)
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

---

## 🔐 Database SSL Configuration

### Aliyun RDS PostgreSQL with SSL

**Configuration** (已启用):
```bash
# backend/.env
DATABASE_URL=postgresql://user:password@host:5432/db?sslmode=verify-ca&sslrootcert=ssl/ApsaraDB-CA-Chain.pem
```

**SSL Modes**:
- `disable` - 不使用SSL (不推荐)
- `require` - 需要SSL但不验证证书
- `verify-ca` - 验证CA证书 (✅ 当前配置)
- `verify-full` - 完整验证 (最安全)

**CA证书位置**: `backend/ssl/ApsaraDB-CA-Chain.pem`

**验证SSL状态**:
```bash
cd backend
source venv/bin/activate
python test_rds_sqlalchemy.py
```

---

## 📊 Security Checklist

Before every commit:

- [ ] No API keys in code or docs
- [ ] `.env` is in `.gitignore` and not staged
- [ ] Pre-commit hook passes
- [ ] No hardcoded passwords
- [ ] No sensitive data in comments
- [ ] SSL certificates (`.pem`, `.crt`) not committed

Before pushing to GitHub:

- [ ] Run `git log -p` to review changes
- [ ] Verify `.env` not in history: `git log --all -- .env`
- [ ] Check for secrets: `gitleaks detect` (if installed)

---

## 🚨 Incident Response

If you discover a security issue:

1. **DO NOT** create a public GitHub issue
2. **Immediately** revoke any exposed credentials
3. Contact project maintainer privately
4. Follow the cleanup steps above

---

## 📜 Security Audit Log

| Date | Issue | Action | Status |
|------|-------|--------|--------|
| 2025-10-06 | API keys in docs | Revoked + Git history rewrite | ✅ Resolved |

---

## 📞 Contact

For security concerns, contact: [Your Contact Info]

**Remember: When in doubt, ask before committing!**
