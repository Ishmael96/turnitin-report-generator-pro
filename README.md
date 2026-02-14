# 🔍 Turnitin Checker - Deployment Guide

## 📋 What You Have

A complete web application for checking plagiarism and AI detection with:
- ✅ Login authentication (you control who gets access)
- ✅ File upload interface
- ✅ PDF report generation
- ✅ Admin dashboard
- ✅ 100% FREE hosting

---

## 🚀 Quick Start Deployment (5 Minutes)

### Step 1: Create GitHub Account
1. Go to [github.com](https://github.com)
2. Click **Sign up** (if you don't have an account)
3. Choose the FREE plan

### Step 2: Create New Repository
1. Click the **+** icon (top right) → **New repository**
2. Repository name: `turnitin-checker`
3. Description: `Plagiarism and AI detection tool`
4. Select **Public**
5. ✅ Check **Add a README file**
6. Click **Create repository**

### Step 3: Upload Files
1. In your new repository, click **Add file** → **Upload files**
2. Drag and drop ALL these files:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/secrets.toml`
   - `.streamlit/config.toml`
3. Add commit message: "Initial commit"
4. Click **Commit changes**

### Step 4: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **Sign in** → Choose **Continue with GitHub**
3. Authorize Streamlit
4. Click **New app**
5. Select:
   - **Repository:** `your-username/turnitin-checker`
   - **Branch:** `main`
   - **Main file path:** `app.py`
6. Click **Deploy!**

### Step 5: Get Your Link! 🎉
After 2-3 minutes, you'll get:
```
https://turnitin-checker.streamlit.app
```

**Share this link with your students!**

---

## 👥 Managing Users (Add/Remove Students)

### To Add a New User:

1. Go to your GitHub repository
2. Navigate to `.streamlit/secrets.toml`
3. Click the **pencil icon** (Edit)
4. Add a new line under `[users]`:
```toml
new_student = "their_password"
```
5. Click **Commit changes**
6. Wait 1-2 minutes for Streamlit to update

### To Remove a User:

1. Edit `.streamlit/secrets.toml`
2. Delete their line
3. Commit changes

### Example secrets.toml:
```toml
admin_password = "your_secure_admin_password"

[users]
john_doe = "pass123"
jane_smith = "pass456"
alex_jones = "pass789"
# Add more users here (up to 20)
```

---

## 🔑 Login Credentials

### For You (Instructor):
- **Username:** `admin`
- **Password:** (what you set in `admin_password`)
- **Access:** Admin dashboard + all features

### For Students:
- **Username:** (what you set in secrets.toml)
- **Password:** (what you set in secrets.toml)
- **Access:** Upload documents and get reports

---

## 📊 Admin Dashboard Features

When you login as **admin**, you can:
- ✅ View usage statistics
- ✅ See list of all users
- ✅ Monitor activity
- ✅ Manage access

---

## 🛠️ Troubleshooting

### App won't start?
- Check that all 4 files are uploaded correctly
- Verify `secrets.toml` is in `.streamlit/` folder
- Check for typos in `secrets.toml`

### User can't login?
- Verify username/password in `secrets.toml`
- Make sure no extra spaces
- Password is case-sensitive

### Need to change admin password?
1. Edit `.streamlit/secrets.toml`
2. Change `admin_password = "new_password"`
3. Commit changes
4. Wait 1-2 minutes

### Want to update the app?
1. Edit `app.py` in GitHub
2. Commit changes
3. Streamlit auto-redeploys (2-3 minutes)

---

## 🎨 Customization

### Change App Name:
Edit `app.py`, line 23:
```python
page_title="Your Custom Name"
```

### Change Colors:
Edit `.streamlit/config.toml`:
```toml
primaryColor = "#YOUR_COLOR"
backgroundColor = "#YOUR_COLOR"
```

### Change Upload Limit:
Edit `.streamlit/config.toml`:
```toml
maxUploadSize = 20  # Max file size in MB
```

---

## 📧 Sharing with Students

### Email Template:
```
Subject: Access to Turnitin Checker

Hi [Student Name],

You now have access to our plagiarism and AI detection tool.

🔗 Link: https://your-app-name.streamlit.app

Your login credentials:
- Username: [username]
- Password: [password]

Please keep your credentials secure and do not share them.

Instructions:
1. Go to the link above
2. Login with your credentials
3. Upload your Word document (.docx)
4. Click "Analyze Document"
5. Download your reports

If you have any issues, please contact me.

Best regards,
[Your Name]
```

---

## 🔒 Security Best Practices

1. **Change default passwords** immediately
2. **Use strong passwords** (mix of letters, numbers, symbols)
3. **Don't share** the admin password
4. **Regularly review** user list
5. **Monitor** usage from admin dashboard

---

## 💰 Cost & Limits

### Streamlit Free Tier:
- ✅ **FREE forever**
- ✅ Unlimited users (you control access)
- ✅ 1GB RAM (plenty for PDFs)
- ✅ Good for ~10 concurrent users
- ✅ 24/7 uptime

### If you exceed free tier:
- Streamlit will email you
- You can upgrade to paid ($20/month) if needed
- Or reduce usage

---

## 📞 Support

### Streamlit Issues:
- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Forum](https://discuss.streamlit.io)

### App Issues:
- Check GitHub repository
- Review error logs in Streamlit Cloud

---

## ✅ Checklist

Before going live:

- [ ] Changed admin password from default
- [ ] Added all student credentials
- [ ] Tested login with admin account
- [ ] Tested login with student account
- [ ] Uploaded a test document
- [ ] Downloaded reports successfully
- [ ] Shared link with students
- [ ] Provided credentials to students

---

## 🎯 Next Steps

1. **Deploy the app** (follow steps above)
2. **Test thoroughly** with a document
3. **Add your students** to secrets.toml
4. **Share credentials** via email
5. **Monitor usage** from admin panel

---

**You're all set! 🎉**

Your Turnitin checker is now live and ready to use!
