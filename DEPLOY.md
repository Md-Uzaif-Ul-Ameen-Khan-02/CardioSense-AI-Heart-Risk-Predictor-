# Deploying CardioSense AI (Streamlit)

## 1. Project structure

```
heart-app/
├── app.py
├── requirements.txt
├── knn_heart.pkl
├── scaler.pkl
├── columns.pkl
└── .streamlit/
    └── config.toml
```

## 2. Run locally first

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501

Tip: pin the same scikit-learn version you used to train the model
(`pip show scikit-learn`, then write e.g. `scikit-learn==1.5.2` in requirements.txt),
otherwise the .pkl files may fail to load.

## 3. Deploy on Streamlit Community Cloud (free)

1. Create a GitHub repo and push the whole folder (including the .pkl files):
   ```bash
   git init
   git add .
   git commit -m "CardioSense AI"
   git branch -M main
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app** -> **Deploy a public app from GitHub**.
4. Choose your repo, branch `main`, main file path `app.py`.
5. Click **Deploy**. First build takes 2-5 minutes; you get a `https://<name>.streamlit.app` URL.

Updates: any `git push` redeploys automatically.

## 4. Alternative: Hugging Face Spaces

1. Create a new Space at https://huggingface.co/spaces, SDK = **Streamlit**.
2. Upload `app.py`, `requirements.txt`, the three `.pkl` files and `.streamlit/config.toml`.
3. The Space builds and goes live automatically.

## 5. Alternative: Render

- New -> Web Service -> connect the repo
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## 6. Common problems

| Problem | Fix |
|---|---|
| `FileNotFoundError: knn_heart.pkl` | Pickle files must be committed in the repo root next to app.py |
| `ModuleNotFoundError` | Add the missing package to requirements.txt |
| Pickle / version error | Pin the same scikit-learn version used for training |
| Files over 100 MB rejected by GitHub | Use Git LFS |
