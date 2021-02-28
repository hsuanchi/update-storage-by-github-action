# GitHub Action 上傳 github repo 至 GCP Storage

## 專案環境

此次使用套件：
```
google-cloud-storage
```


此次專案資料夾結構：
```

├── README.md
├── main.py
├── forder # 測試單層 folder
│   └── test.html
└── static # 測試多層 folder
    ├── css
    ├── js
    └── media
```


## 步驟一. GCP Sotrage 設定

1. 創建 Bucket

首先創建 Bucket，未來的網址 url 會與此命名有直接關係，例如這邊取名為 `demo-2021`，未來存取資料的 url 會是像這樣： `https://storage.googleapis.com/demo-2021/README.md`
<img src="https://github.com/hsuanchi/update-storage-by-github-action/blob/main/image/step1 - 建立GCP Storage Bucket.jpg">

2. 設定檢視權限

接下來我們會將此 Bucket 的權限設定為，
所有人都可以檢視，所以記得不要將機密資料放置於此 Bucket 內
<img src="https://github.com/hsuanchi/update-storage-by-github-action/blob/main/image/step2 - 設定 bucket 檢視權限.jpg">


3. 取得憑證金鑰

最後我們會需要上傳或更新檔案至此 Bucket，所以需要申請憑證，待會在 Python 的 code 中會使用到此憑證。

https://console.cloud.google.com/apis/credentials

<img src="https://github.com/hsuanchi/update-storage-by-github-action/blob/main/image/step3 建立 GCP 憑證鑰匙.jpg">


## 步驟二. 設定 GitHub Action

我們會在 project 位置中的 `.github/workflows/` 新增一個 [automatic_update.yml](https://github.com/hsuanchi/update-storage-by-github-action/blob/main/.github/workflows/automatic_update.yml) 檔案

這邊設定觸發條件是當 branch main 被 push 時觸發，當然你可以改成 pull 或是其他的 branch，甚至可以是定時任務[on.schedule](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#onschedule)
```
name: Build and Deploy to Google Cloud Storage

on:
  push:
    branches:
    - main
```

使用 github 託管的 
Virtual environment，想修改 `ubuntu-latest` 的話可以參考這篇 [Specifications for GitHub-hosted runners](https://docs.github.com/en/actions/reference/specifications-for-github-hosted-runners)
```
jobs:
  setup-build-deploy:
    name: Setup and Upload
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 4
      matrix:
        python-version: [3.7]
```

接下來首先使用 public action `actions/checkout@v2` 來建立 python 環境，再使用 `google-github-actions/setup-gcloud@master` 來通過 gcloud 的憑證，最後再執行我們寫好的 `main.py` 腳本
```
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}

    - name: Set up gcs account_key
      uses: google-github-actions/setup-gcloud@master
      with:
        service_account_key: ${{ secrets.GCP_CREDENTIALS }}
        export_default_credentials: true

    - name: Install google-cloud-storage
      run: |
        python -m pip install --upgrade pip
        pip3 install google-cloud-storage
    - name: Run upload
      run: |
        python3 main.py
```

完整 code 存放在 [automatic_update.yml](https://github.com/hsuanchi/update-storage-by-github-action/blob/main/.github/workflows/automatic_update.yml)

## 步驟三. Python upload GCP Storage 程式

首先定義一下變數：

* local_path: 本地要上傳資料夾的位置
* bucket_name: 上傳至 GCS Bucket 的位置
* bucket_forder: 上傳至 GCS Bucket 內的特定資料夾
* ignore_list: 這邊是排除清單

```
local_path = "."
bucket_forder = ""
bucket_name = "demo-2021"
ignore_list = ["venv", key_name]
```

因為 GCP Sorage API 並沒有提供一次上傳完整資料夾的功能，只能單筆上傳，所以這邊寫了一個遞迴，來上傳資料夾：
```
def upload_folder_to_gcs(local_path, bucket, gcs_path):
    assert os.path.isdir(local_path)

    for local_file in glob.glob(local_path + "/**"):

        if not os.path.basename(local_file) in ignore_list:
            if not os.path.isfile(local_file):
                upload_folder_to_gcs(
                    local_file,
                    bucket,
                    gcs_path + "/" + os.path.basename(local_file),
                )
            else:
                remote_path = os.path.join(gcs_path, local_file[1 + len(local_path) :])
                blob = bucket.blob(remote_path)
                blob.upload_from_filename(local_file)
                print(f'Uploaded {local_file} to "{bucket_name}" bucket. {remote_path}')
```
更多關於 GCS 的 CRUD 操作可以參考官方的這篇 [python-docs-samples/storage/](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/storage/cloud-client)

關於完整 Python code 存放在 [main.py](https://github.com/hsuanchi/update-storage-by-github-action/blob/python-script-upload/main.py)


最後只需要 `git push` 就可以看到以下畫面囉，然後再去 google cloud storage 確認有沒有上傳的檔案就完成了！

<img src="https://github.com/hsuanchi/update-storage-by-github-action/blob/main/image/github action check.jpg">

