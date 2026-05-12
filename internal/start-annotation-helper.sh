source .venv/bin/activate
rm -rf my_backend
label-studio-ml init my_backend --script label_assist.py
cp ../assets/papermd-tuesday-12-may-build.pt ./my_backend/latest-model.pt
label-studio-ml start ./my_backend
